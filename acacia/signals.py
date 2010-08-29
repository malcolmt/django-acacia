from django import dispatch

# FIXME: Document!
pre_merge = dispatch.Signal(providing_args=["merge_pairs"])

# FIXME: Document!
pre_move = dispatch.Signal(providing_args=["moving"])

