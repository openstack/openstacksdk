# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import warnings

sys.path.insert(0, os.path.abspath('../..'))
sys.path.insert(0, os.path.abspath('.'))

# -- General configuration ----------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    'sphinx.ext.autodoc',
    'openstackdocstheme',
    'sphinxcontrib.rsvgconverter',
]

# openstackdocstheme options
openstackdocs_repo_name = 'openstack/openstacksdk'
openstackdocs_pdf_link = True
openstackdocs_use_storyboard = True
html_theme = 'openstackdocs'

# autodoc generation is a bit aggressive and a nuisance when doing heavy
# text edit cycles.
# execute "export SPHINX_DEBUG=1" in your terminal to disable

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
copyright = u'2017, Various members of the OpenStack Foundation'

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = True

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'native'

autodoc_member_order = "bysource"

# Locations to exclude when looking for source files.
exclude_patterns = []

# -- Options for HTML output ----------------------------------------------

# Don't let openstackdocstheme insert TOCs automatically.
theme_include_auto_toc = False

# Output file base name for HTML help builder.
htmlhelp_basename = 'openstacksdkdoc'

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass
# [howto/manual]).
latex_documents = [
    ('index',
     'doc-openstacksdk.tex',
     u'OpenStackSDK Documentation',
     u'OpenStack Foundation', 'manual'),
]

# Allow deeper levels of nesting for \begin...\end stanzas
latex_elements = {'maxlistdepth': 10}

# Disable usage of xindy https://bugzilla.redhat.com/show_bug.cgi?id=1643664
latex_use_xindy = False

# Include both the class and __init__ docstrings when describing the class
autoclass_content = "both"
