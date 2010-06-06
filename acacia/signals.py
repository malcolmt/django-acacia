from django import dispatch

pre_merge = dispatch.Signal(providing_args=["merge_pairs"])

