import skppy, skppy.parser.scenes_parser as sp
_orig = sp._scene_reference_ids
def _seguro(records, tag):
    try: return _orig(records, tag)
    except Exception: return []
sp._scene_reference_ids = _seguro
def carregar(p="Farmhouse.skp"): return skppy.load(p)
