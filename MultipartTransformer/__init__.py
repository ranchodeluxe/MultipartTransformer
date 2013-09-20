# -*- coding: utf-8 -*-
def classFactory(iface):
    # load MultipartTransformer class from file MultipartTransformer
    from multiparttransformer import MultipartTransformer
    return MultipartTransformer(iface)
