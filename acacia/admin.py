from django import forms
from django.contrib import admin

import models

class TopicForm(forms.ModelForm):
    """
    Instead of displaying the standard model fields in the admin, display the
    name field and a synthesised "parent" field. The TopicAdmin class then
    converts uses these fields to make the appropriate modifications to the
    underlying Topic instances.
    """
    parent = forms.ModelChoiceField(models.Topic.objects.all(), required=False,
            empty_label="<root node>")

    class Meta:
        model = models.Topic
        fields = ("name", "parent")

    def __init__(self, *args, **kwargs):
        """
        In addition to normal ModelForm initialisation, sets the initial value
        of the "parent" form field to be correct for any passed in instance and
        removes any descendants of the initial instance as possible parent
        choices.
        """
        super(TopicForm, self).__init__(*args, **kwargs)
        if self.instance.pk is not None:
            parent = self.instance.get_parent()
            parent_field = self.fields["parent"]
            parent_field.initial = parent and parent.pk or None
            parent_field.queryset = models.Topic.objects.exclude(
                    path__startswith=self.instance.path)

    def save_m2m(self):
        """
        The admin expects to have indirectly called
        TopicForm.save(commit=False) and will then call this method (it's
        created as a result of commit=False). So it has to be stubbed out, but
        we don't need to do anything here.
        """
        pass


class TopicAdmin(admin.ModelAdmin):
    # XXX: Duplicates the field definitions from the ModelForm, which should be
    # unnecessary. Probably a Django admin bug (if I omit this, every field is
    # shown in the admin form).
    fields = ("name", "parent")
    form = TopicForm

    def save_form(self, request, form, change):
        """
        Returns the updated and unsaved instance of the model being changed or
        added. This instance isn't fully complete in our case, since attributes
        are updated when it is saved (as part of the tree structure).
        """
        name = form.cleaned_data["name"]
        parent = form.cleaned_data.get("parent")
        if change:
            # Changing an existing instance.
            instance = form.instance
            instance.name = name
        else:
            # Adding a new instance.
            instance = models.Topic(name=name)

        # The full name is set to the *new* full_name, so that it appears
        # correctly in the history logs, for example.
        if parent:
            instance.full_name = "%s%s%s" % (parent.full_name,
                    models.Topic.separator, name)
        else:
            instance.full_name = name
        return instance

    def save_model(self, request, instance, form, change):
        """
        Add the new instance node to the tree at the appropriate point.
        """
        parent = form.cleaned_data.get("parent")
        if change:
            # Changing an existing topic.
            moved = False
            if instance.depth != 1:
                if not parent:
                    # Move a non-root node to the root.
                    root = models.Topic.get_first_root_node()
                    instance.move(root, "sorted-sibling")
                    moved = True
                elif parent.id != instance.get_parent().id:
                    # Move a non-root node to a different, non-root, parent.
                    instance.move(parent, "sorted-child")
                    moved = True
            else:
                if parent:
                    # Move a root node to a lower point in the tree.
                    instance.move(parent, "sorted-child")
                    moved = True
            if moved:
                # Refresh from the database, as any moves will have changed the
                # depth and path values.
                instance = models.Topic.objects.get(pk=instance.pk)
            instance.save()
        else:
            # Adding a new instance.
            if not parent:
                models.Topic.add_root(instance)
            else:
                parent.add_child(instance)

admin.site.register(models.Topic, TopicAdmin)

