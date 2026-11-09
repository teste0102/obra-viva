# MANUAL DE CONSTRUÇÃO — Obra Viva (casa e castelo)

> Para usar num chat novo, diga só: **"leia o manual de construção"**.
> Escrito em 08/11/2026 para o próprio Claude ler no começo de uma conversa nova. Atualizar sempre que algo novo for aprendido (ver seção 12).

---------------------------------------------------------------------

## 1. O que é o projeto

Vídeos de **time-lapse de obra fotorrealista** (câmera fixa, 9 fases) seguidos de um **giro de drone** ao redor da construção pronta. Tudo roda no **servidor** do usuário, em pipelines desligados do PC (retomáveis).

| Projeto | Estado | Observação |
|---|---|---|
| **Casa** (Southern Farmhouse, Jay Osborne, CC BY-SA 4.0 — dar crédito, freefarmhouse.com) | Pronta. Último vídeo: `obra_giro17` (955 quadros, 1664x1248, 16 fps) | Adaptada para ficar **rente ao chão** (original é elevada) |
| **Castelo** de pedra | Muralhas prontas em 5 trechos (`castelo1`, 400 quadros). Faltam torres de canto, torre de menagem e acabamentos finos | Medidas inventadas; o usuário vai procurar a **planta** |

Queixa original do usuário: vídeo "muito Lego/desenho". Meta: parecer obra de verdade.

---------------------------------------------------------------------

## 2. Regras do usuário (valem sempre)

1. **Plano de checagens:** ao disparar qualquer execução demorada (render, Wan, download, ampliação, junção ffmpeg), dizer na mesma mensagem 3–4 horários de checagem e avisar sem ele perguntar. Vale também para etapas fora do ComfyUI (a fila do ComfyUI fica vazia mas a GPU está ocupada — explicar isso).
2. **Vídeo:** ao citar um vídeo, dar o **link clicável completo** E enviar o arquivo no chat. Nunca só o caminho.
3. **Linguagem simples.** O usuário não é técnico.
4. **Nunca apagar nada sem ele dizer.** Limpezas só com o comando dele.
5. **Workflows sempre dentro de pasta.** Nada solto na raiz de `workflows/` do ComfyUI; **cada projeto abre uma pasta nova** (Construcao, Castelo, Danca e animacao...) e os workflows daquele projeto ficam dentro. Conferir depois de salvar.
6. **Máxima qualidade possível**, sem propor "pular etapa" ou "esperar" (ele paga o Claude para isso). Ser proativo.
7. Quando ele diz "o resto está perfeito", **refazer só o trecho apontado** (o cache do ComfyUI deixa barato).
8. **Linhas retas devem ficar retas** (guarda-corpo, ameias, fileiras de pedra). Realismo máximo: "não é sítio, é casa".
9. Quando ele autorizar um bloco de tentativas (ex.: "8 testes do castelo, sem pedir permissão"), seguir direto, mas só aquele bloco.
10. Corrigir o que o usuário apontar com **a causa real**, não suposição (erro já cometido: achei que o bloco cinza embaixo da casa era alucinação do Wan; era a camada "SAIA" do composite).

---------------------------------------------------------------------

## 3. Onde estão as coisas

### Servidor
- Acesso: `ssh -p PORTA USUARIO@SERVIDOR`. ComfyUI em `http://SERVIDOR_IP:8188` (**só no IP da LAN**, não em 127.0.0.1). GPU RTX 5060 Ti 16 GB. Disco ~79 GB livres (91%).
- **Casa (scripts):** `~/ferramentas/blender/` (cenas `cena_*.py`, composições `compoe_*.py`, pipelines `pipeline_*.py/.sh`, correções `fix*.sh`, `finaliza2.sh`, `recolor_chamine.py`, `roda_foto_srv.py`, `roda_flf_srv6.py`, `roda_fun_srv6.py`/`roda_fun_srv7.py`).
- **Castelo (scripts):** `~/ferramentas/castelo/` (`cena_castelo.py`, `t1.sh`, `t2.sh`, `v1.sh`, `v2.sh`, `fim1.sh`, `ampliar.py`, `roda_*.py`, texturas em `tex/`).
- **Modelo 3D da casa:** `~/ferramentas/skp/out/farmhouse3.obj` (exportado do `Farmhouse.skp` com `exporta_obj3.py`; camadas separadas, nomes `<camada>@<FD|L1|L2|RF>`).
- **Blender:** `~/blender/blender-4.5.15-linux-x64/blender` (rodar com `-b --factory-startup --python script.py -- args`). Cycles OPTIX.
- **Saídas:** `/opt/comfy/ComfyUI/output/<pasta>/`. Casa: `construcoes16` … `construcoes39` (final em `construcoes39/obra_giro17_2x.mp4` e `_leve.mp4`). Castelo: `output/castelo/` (`castelo1_2x.mp4`, `castelo1_leve.mp4`, fotos `t2_F*`, `t3_F1`, trechos `c_seg_0N`).
- **Entradas do ComfyUI:** `/opt/comfy/ComfyUI/input/` (copiar com `sudo -n -u comfy cp <caminho relativo> ...`).
- **Workflows:** `/opt/comfy/ComfyUI/user/default/workflows/` com as pastas: `Construcao` (21 arquivos: Construções 2 a 18 + LEIA-ME), **`Castelo`** (cópia da Construções 18 + LEIA-ME + `scripts_castelo/`), `Danca e animacao` (9), `Favoritos` (7), `Geral` (21), `Backup` (13), `NSFW` (5), `Qwen Image 2.1` (4), `Z-Image` (1), `gerador_video_instagram` (4).

### PC do usuário
- `Desktop\Ferramentas ComfyUI\projeto-casa-farmhouse` (repositório git local → GitHub `teste0102/obra-viva`; forks de ferramentas com prefixo `obra-viva-*`).
- `Desktop\Conversa Obra Viva - resumo organizado.md` (resumo da casa até 06/11).
- `Desktop\os Pytons\` (app Python do usuário; aba "10. Publicar no Instagram" feita, **não testada ao vivo**, falta token/IG id).
- Projeto original: `Desktop\1click\casa projetos contrução\` (PDF e .skp).

---------------------------------------------------------------------

## 4. Método geral (serve para qualquer construção)

1. **Geometria exata em 3D** (Blender). A IA não guarda geometria: ela redesenha. Por isso o 3D manda e a IA só dá a "pele" fotorrealista.
2. **9 fases** renderizadas com a **mesma câmera fixa** (terreno vazio → fundação → piso → paredes → ... → pronta).
3. **Foto realista por fase:** Qwen-Image-Edit 2511 + LoRA `bigly_merge_1` (Qwendle) força **0,7**, **denoise 0,85** (`roda_foto_srv.py`, env `DENO` e `PROMPT`). Prompt começa "Turn this 3D render into a real photograph… keep exactly the same camera angle, composition, shapes and positions… add nothing else".
4. **Vídeo entre fases:** Wan 2.2 primeiro/último quadro (`roda_flf_srv6.py`), 832x624, 81 quadros, 4 passos (Lightning, cfg 1), trecho a trecho. **Com cfg 1 o prompt negativo é ignorado:** o que vale é o positivo (ex.: frase "no cars, no vehicles").
5. **Giro de drone:** guia 3D do Blender (sem árvores) → Wan 2.2 **Fun Control** (`roda_fun_srv6/7.py`), com foto Qwen do primeiro quadro como referência. 3 trechos de 81 quadros (az -38→32→102→172), xfade 0,25 s.
6. **Composições exatas por cima** do vídeo do Wan para o que ele deforma (guarda-corpo, telhado, porta, chaminé): `compoe_gc.py`, `compoe_obra.py`, `compoe_telhado.py`, `compoe_porta.py`, `recolor_chamine.py`.
7. **Ampliação 2x:** 4x-UltraSharp reduzido a 2x (1664x1248). Rodar com `sudo -n -u comfy /opt/comfy/venv/bin/python` e **o script e a entrada em `/tmp`** (o usuário `comfy` não lê `/home/USUARIO`). Script atual do castelo: `ampliar.py` (≈ 8 min para 400 quadros; o antigo `/tmp/ampliar_video2.py` sumiu).
8. **Montagem final:** ffmpeg concat/xfade; versão leve (crf 24) para enviar; completa ampliada para guardar.

---------------------------------------------------------------------

## 5. Lições da CASA (o que não funcionou e por quê)

- **Câmera calibrada** a partir da perspectiva do autor (erro ~6 px) deu o primeiro modelo; **o modelo real do .skp** (via `skppy` em container, depois OBJ) resolveu o giro (casa idêntica de todos os ângulos). Antes, o Qwen "mudava o projeto" a cada ângulo.
- **Operários grandes demais:** colocar a frase de escala em TODOS os trechos ("six feet tall, heads reach two thirds of the wall, far from the camera").
- **Ampliação borrou rostos de muita gente:** pedir poucos operários, longe, devagar, sem "very fast motion".
- **Grafo único com 16 trechos morreu por OOM** → rodar **trecho a trecho**.
- **Guarda-corpo torto:** Wan deforma balaústres finos. Solução: renderizar só o guarda-corpo no Blender e compor por cima; apagar o torto por abertura morfológica.
- **Casa rente ao chão** (decisão do usuário): `SOLO_Z=0.40`, `SEM_FUND=1`, laje de concreto na fase 1.
- **Blocos cinzas embaixo da estrutura:** causa = composição **"SAIA"** em `compoe_obra.py` na fase 8. Correção: `NO_SAIA=1`.
- **Árvores no fim do giro sumiam:** o guia sem árvores fazia o Wan apagá-las. O Wan **copia formas do guia literalmente**: árvores-proxy viram bolas/topiaria/cerca-viva. Solução ("guia suave"): casa nítida do render sem árvores + árvores do render com árvores **borradas só nos pixels de árvore** (`/tmp/suave.py`, sigma 14), carvalhos pequenos/distantes perto do horizonte, prompt do Qwen pedindo carvalhos naturais, céu aberto, sem topiaria. Scripts: `cena_orbita_m.py` (env `MATA=1`), `roda_fun_srv7.py`, `fix7.sh`, `comp_s3.sh`, `finaliza2.sh`.
- **Quando o Qwen recebe a foto final como imagem 1**, ele constrói demais; usar o terreno vazio ou o desenho como base.
- **Denoise:** 0,85 mantém realismo e balaústres retos; ≤0,75 perde realismo.
- **LoRAs no servidor:** `bigly_merge_1` (Qwendle), `iPhone_Realism_v0.9`, `Amature realism`, Lightning (Wan e Qwen), orbit/drone do Wan, multiple-angles do Qwen.
- **Ferramentas instaladas:** SeedVR2 (pesos baixados, ainda não comparado ao UltraSharp), `comfyui_controlnet_aux`, kjnodes, videohelpersuite.

---------------------------------------------------------------------

## 6. Lições do CASTELO (08/11)

- **Material:** textura Poly Haven (CC0) **`castle_brick_07`** (ESC=3) deu a alvenaria mais regular: blocos grandes em fileiras certinhas. As outras testadas: `stone_brick_wall_001` (mais rústica), `large_sandstone_blocks_01`.
- **Cena 3D:** `cena_castelo.py` — muralha 34 x 26 m, espessura 2,4 m, 9 m de altura, ameias 1,5 m com vão 1 m, câmera az -38 el 9 R 58 lente 35. Fases: 0 terreno, 1 plinto, 2/3/4 muralha 3/6/9 m (com andaimes), 5 ameias, 6 portal (bloco com arco redondo recortado + anel de aduelas + portas de carvalho com tiras de ferro, ameias sobre o portal), 7 bases das torres de canto, 8 menagem.
- **Cuidado de acabamento (pedido do usuário): portas e portão.** O arco com aduelas e as portas escuras ficaram bons. Prompt da fase 6 descreve "carved voussoir stones" e "heavy dark oak double doors with black iron straps".
- **Fundação (fase 1):** o 1º prompt fez o Qwen inventar uma muralha inteira ao fundo. Corrigir dizendo explicitamente que **nada existe atrás**, só terra, pasto e árvores.
- **Wan:** 5 trechos FLF (F1→F2→F3→F4→F5→F6). O trecho 2 gerou um **carro prateado**: refeito com "no cars, no vehicles" e outra semente. No trecho final há um vulto branco perto do portão (pendente).
- **Tempos medidos:** render Blender 1664x1248 ≈ 1 min; foto Qwen 30–60 s; trecho Wan ≈ 4,5 min; ampliação 400 quadros ≈ 11 min.
- **Pendente:** torres de canto (cilindros), menagem, ameias nas torres, acabamento fino das portas/janelas, planta real, refazer o trecho do portão (vulto).

---------------------------------------------------------------------

## 7. Armadilhas técnicas

- Python do PC: só PowerShell (`python` com PIL e `imageio_ffmpeg`; **sem cv2**). ffmpeg local: `…\Python\pythoncore-3.15-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v9.0.2.exe`. No git-bash não há python.
- Servidor: venv `/opt/comfy/venv/bin/python` tem cv2/numpy/torch/spandrel; `python3` do sistema também existe.
- **`sudo -n -u comfy`** para escrever na pasta output. `comfy` não entra em `/home/USUARIO`: arquivos de entrada/script em `/tmp` com `chmod a+r`.
- Interromper job do ComfyUI: `POST /interrupt` e `POST /queue {"clear":true}` em `SERVIDOR_IP:8188`.
- **Nunca `pkill -f` com texto que está no próprio comando ssh** (mata a própria sessão). Usar `ps -eo pid,args | awk '/[x]yz.sh/{print $1}'` e `kill`.
- Lançar desligado: `(setsid nohup ./script.sh >out 2>&1 </dev/null &)`.
- Trocar o prompt no meio do ComfyUI apaga o cache do grafo anterior.
- `baixar.py` não cria pasta destino: criar antes.
- Docker: containers `loja_*` e `frigate` não são do projeto: **não mexer**; nunca `prune -a`.
- Monitor (≤30 min) com `tail -f | grep`; notificações antigas de Monitor expirado são inofensivas.

---------------------------------------------------------------------

## 8. Workflows (inventário em 08/11/2026)

Salvos em `/opt/comfy/ComfyUI/user/default/workflows/`:
- **Construcao (21):** `Construcoes - casa (...)` (3 versões iniciais), `Construcoes 2` a `Construcoes 18` (18 = versão longa com giro de drone, a mais atualizada) e `LEIA-ME.md`.
- **Castelo (3):** `Castelo 0 - base copiada da Construcoes 18 (ponto de partida).json`, `LEIA-ME.md`, pasta `scripts_castelo/`. **Ainda não há workflow próprio do castelo**: os pipelines reais são os scripts em `~/ferramentas/castelo/`.
- Demais pastas: Danca e animacao (9), Favoritos (7), Geral (21), Backup (13), NSFW (5), Qwen Image 2.1 (4), Z-Image (1), gerador_video_instagram (4).
- Para salvar um workflow novo: `POST /api/userdata/workflows%2F<Pasta>%2F<nome>.json?overwrite=true`; conferir com `GET /api/userdata?dir=workflows&recurse=true&split=false` que nenhum ficou sem pasta.

---------------------------------------------------------------------

## 9. Receita para um novo projeto de construção

1. Perguntar/obter o projeto (planta, modelo 3D ou referência) e o material.
2. Criar **pasta nova** em `workflows/` e em `~/ferramentas/<projeto>/` (copiar `roda_foto_srv.py`, `roda_flf_srv6.py`, `roda_fun_srv7.py`, `construcoes18_api.json`).
3. Modelar a cena em Blender com fases e câmera fixa; texturas CC0 (Poly Haven).
4. Fotos por fase (Qwen + Qwendle 0,7, denoise 0,85), conferir a alvenaria e corrigir o prompt.
5. Trechos Wan FLF (um por vez), conferir quadros, refazer só o que errar (sem carros/pessoas extras).
6. Composições exatas do que for fino/repetitivo.
7. Giro de drone (Fun Control) com guia suave.
8. Ampliar 2x, juntar, enviar leve + link.
9. Atualizar este manual e a memória.

---------------------------------------------------------------------

## 10. Pendências em aberto (08/11)

- Castelo: torres de canto, menagem, acabamento, planta, vulto do portão, giro de drone do castelo, workflow próprio.
- Casa: trecho final com leve faixa clara no horizonte esquerdo do último quadro; só foram vistos quadros amostrados.
- Instagram: testar a aba com token real.
- Atualizar o resumo do Desktop e o repositório `obra-viva` no GitHub com os scripts novos (castelo, NO_SAIA, guia suave).
- Limpeza do servidor (arquivos `.bak`, pastas `old_fix*`, `opencut-classic`, imagem `python:3.12-slim`) **só quando o usuário mandar**.

---------------------------------------------------------------------

## 11. Atualizar este manual

Ao terminar uma etapa importante: acrescentar o que funcionou, o erro e a causa real, e a data. Manter cópias iguais em: Desktop (este arquivo), `~/ferramentas/MANUAL_CONSTRUCAO.md` no servidor e nas pastas `workflows/Construcao` e `workflows/Castelo`.
