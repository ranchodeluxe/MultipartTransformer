# -*- coding: utf-8 -*-
def classFactory(iface):
    import sip
    sip_qvariant = 1
    try:
        sip_qvariant = sip.getapi("QVariant")
    except Exception:
        pass

    if sip_qvariant > 1:
        # Use the new API style
        # load MultipartTransformerv20 class from file MultipartTransformer_v20
        from multiparttransformer_v20 import MultipartTransformerv20
        return MultipartTransformerv20(iface)
    else:
        # Use the old API style
        # load MultipartTransformer class from file MultipartTransformer
        from multiparttransformer import MultipartTransformer
        return MultipartTransformer(iface)
