{{ fullname | escape | underline}}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}
 
   .. rubric:: {{ _('Methods') }}

   .. autosummary::
      ~{{ name }}.{{ item }}

   .. rubric:: {{ _('Attributes') }}

   .. autosummary::
      ~{{ name }}.{{ item }}
