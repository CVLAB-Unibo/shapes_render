"""
Module containing generic utils.

Author: Riccardo Spezialetti
Mail: riccardo.spezialetti@unibo.it
"""
import bpy  # type: ignore


def remove_objects() -> None:
    """
    Remove all the objects in the scene.
    """
    for item in bpy.data.objects:
        bpy.data.objects.remove(item)
