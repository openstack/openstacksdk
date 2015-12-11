# -*- coding: utf-8 -*-
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

import openstackdocstheme

sys.path.insert(0, os.path.abspath('../..'))
# -- General configuration ----------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
]

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
project = u'python-openstacksdk'
copyright = u'2015, OpenStack Foundation'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# "version" and "release" are used by the "log-a-bug" feature
#
# The short X.Y version.
version = '1.0'
# The full version, including alpha/beta/rc tags.
release = '1.0'

# A few variables have to be set for the log-a-bug feature.
#   giturl: The location of conf.py on Git. Must be set manually.
#   gitsha: The SHA checksum of the bug description. Extracted from git log.
#   bug_tag: Tag for categorizing the bug. Must be set manually.
#   bug_project: Launchpad project to file bugs against.
# These variables are passed to the logabug code via html_context.
giturl = u'http://git.openstack.org/cgit/openstack/python-openstacksdk/tree/doc/source'
git_cmd = "/usr/bin/git log | head -n1 | cut -f2 -d' '"
gitsha = os.popen(git_cmd).read().strip('\n')
bug_tag = "docs"
# source tree
pwd = os.getcwd()
# html_context allows us to pass arbitrary values into the html template
html_context = {"pwd": pwd,
                "gitsha": gitsha,
                "bug_tag": bug_tag,
                "giturl": giturl,
                "bug_project": "python-openstacksdk"}

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = True

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

autodoc_member_order = "bysource"

# Locations to exclude when looking for source files.
exclude_patterns = []

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'openstackdocs'

# Add any paths that contain custom themes here, relative to this directory.
html_theme_path = [openstackdocstheme.get_html_theme_path()]

# Don't let openstackdocstheme insert TOCs automatically.
theme_include_auto_toc = False

# Output file base name for HTML help builder.
htmlhelp_basename = '%sdoc' % project

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass
# [howto/manual]).
latex_documents = [
    ('index',
     '%s.tex' % project,
     u'%s Documentation' % project,
     u'OpenStack Foundation', 'manual'),
]

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {'http://docs.python.org/3/': None}

# Include both the class and __init__ docstrings when describing the class
autoclass_content = "both"
