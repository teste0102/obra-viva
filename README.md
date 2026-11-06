# Casa Farmhouse: da planta do SketchUp ao vídeo realista

Vídeo de obra em time-lapse e giro de drone de uma casa de verdade (Southern Farmhouse), feito a partir da **geometria real** do projeto, com render no Blender e acabamento por IA no ComfyUI.

> **Crédito do projeto arquitetônico:** *Southern Farmhouse*, de **Jay Osborne** (freefarmhouse.com), licença **CC BY-SA 4.0**.
> Os vídeos e imagens derivados devem manter o crédito ao autor e a mesma licença. O arquivo `.skp` **não** está neste repositório (baixe do autor).

## Ideia central

A IA sozinha não mantém uma casa consistente quando a câmera gira (a varanda vira telhado, o guarda-corpo entorta). A solução:

1. **Geometria exata** do `.skp` lida com Python puro (`skppy`) e exportada para OBJ (`skp/`).
2. **Render no Blender** (Cycles, GPU) das fases da obra e do giro da câmera (`blender/`).
3. **IA só para o acabamento**: Qwen-Image-Edit 2511 + LoRA de realismo transforma o render em foto (com `denoise` 0,85 para preservar a geometria) e o Wan 2.2 anima (`comfyui/`).

## Fluxo

```
Farmhouse.skp --skppy (container)--> farmhouse3.obj  (camadas separadas por altura: FD/L1/L2/RF)
        |
        +--> blender/cena_fases.py  : 9 fases da obra (fundação ... janelas/portas) no ângulo A
        +--> blender/cena_orbita.py : órbita da câmera (guia do Wan, sem árvores) + quadro inicial em alta
                |
                v
   comfyui/roda_foto_srv.py   : render -> foto realista (Qwen-Edit 2511, LoRA Qwendle 0,7, denoise 0,85)
   comfyui/roda_flf_srv.py    : Wan 2.2 primeiro/último quadro (trechos da obra)
   comfyui/roda_fun_srv.py    : Wan 2.2 Fun Control (giro, guiado pelo render do Blender)
   comfyui/pipeline_giro2.py  : encadeia os 3 trechos do giro + junção + ampliação 2x
   comfyui/pipeline_obra.py   : encadeia as 9 fases + 9 trechos + ampliação + emenda com o giro
```

Os dois `pipeline_*.py` rodam **no próprio servidor**, desligados do PC (`nohup setsid python3 -u pipeline_X.py`), e são **retomáveis**: pulam o que já existe.

## Ângulo e parâmetros que funcionaram

- Câmera: azimute -38°, elevação 5°, distância 33 m, lente 35 mm, centro (0, -1, 5) m. Mostra as duas sacadas, janelas e portas, o telhado e a base.
- Guia do Wan **sem árvores** (copas em 3D viram "bolas de topiaria"); o fundo vem da foto de referência. Árvores só em anel a 75-95 m.
- `denoise` 0,85 nas fotos: o mesmo realismo da IA livre, com guarda-corpos mais retos. Abaixo de 0,75 a foto perde realismo.
- Cada trecho do giro usa **uma foto nova** tirada do render no início do trecho (encadear o último quadro do vídeo anterior acumula deriva de cor).
- Guarda-corpo = madeira aparente de acabamento: balaústres retos, cantos chanfrados (nó *Bevel* no material), espaçamento uniforme.

## Como usar (resumo)

Pré-requisitos: ComfyUI com Qwen-Image-Edit 2511 (+ LoRA Lightning 4 passos), Wan 2.2 I2V e Fun Control (+ LoRAs lightx2v), LoRA de realismo `bigly_merge_1` (Qwendle), Blender 4.5 LTS, FFmpeg. Defina `COMFY_URL` (padrão `http://127.0.0.1:8188`).

```bash
# 1) exportar o modelo (num container Python com skppy e numpy)
python skp/exporta_obj3.py out/farmhouse3        # lê Farmhouse.skp, grava OBJ+MTL em metros, Z para cima

# 2) fotos e vídeos (no servidor)
python3 comfyui/pipeline_giro2.py
python3 comfyui/pipeline_obra.py                 # espera o giro terminar
```

Os caminhos dos scripts assumem `~/ferramentas/blender` e `~/ferramentas/skp` no servidor; ajuste no topo de cada arquivo.

## Lições (resumo)

- O `skppy` 0.10 (beta) quebra ao ler a lista de camadas escondidas das cenas; `skp/carrega.py` contorna isso sem alterar o pacote. A camada `16 - structure` do modelo não tem geometria.
- Componentes espelhados invertem as normais; o exportador calcula a normal pela geometria final e inverte os vértices quando a matriz é espelhada.
- Container sem internet: use `docker run --network host`.
- Operários: o Wan os desenha grandes demais; a frase "six feet tall, heads reach two thirds of the wall height, far from the camera" no texto de cada trecho corrige a escala.
- Em fusão (xfade) entre vistas diferentes da casa aparece "dupla exposição"; prefira corte seco quando a pose de câmera muda.

## O que **não** está aqui

Modelos (`*.safetensors`, `*.pth`), o `.skp`/`.obj` do projeto, vídeos, imagens e qualquer chave de API (`config.json`).
