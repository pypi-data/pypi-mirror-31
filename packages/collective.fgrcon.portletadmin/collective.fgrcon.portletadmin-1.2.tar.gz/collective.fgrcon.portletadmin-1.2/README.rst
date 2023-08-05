

==============================
collective.fgrcon.portletadmin
==============================

collective.fgrcon.portletadmin allows to get an overwiew of all portlet assignments within a Plone site
 or subtree thereof. Furthermore it offers links for editing, moving or deleting any individual portlet.

Please use it at your own risk - backup before usage. It was developed for Plone 5.1.

Features
--------

The addon provides a view: *@@portlet-admin* which can be appended to site root or any subfolder of the site.

 - it lists all portlet assignments on all containers within the selected range recursively
 - for each listed container it provides a link to view the container/page
 - for each existing portlet manager in the container it lists all assigned portlets
 - for each portlet listed there is:
 
   * a link to edit the portlet directly
   * a link to remove (delete) the portlet
   * an option to move the portlet assignment to a different portlet manager within the same or a different container.
     (when selecting a different target container the available portlet managers will be fetched via an AJAX call.)

Examples /Documentation
-----------------------

 - See all portlet assignments of the whole site 
   e.g.: http://Server/Plone/@@portlet-admin
   
   .. image:: ./docs/screen-all-overview.jpg
   .. image:: ./docs/screen-all-detail.jpg
   
 - See all portlet assignments in Folder 1 an below only
     
   .. image:: ./docs/screen-folder1.jpg
   
   Move Collection portlet from right portlets in /Plone/folder1/page1-in-folder-one to left-portlets in 
   /Plone/folder1 (parent)
   
   .. image:: ./docs/screen-move_portlet.jpg

 - *Virtual Hosting*
    The addon can handle something like http://1.2.3.4:8080/Plone and mapped this (rewritten) as http:/example.org
    

Translations
------------

This product is available in English only  - its just an utility not ment for end users.



Installation
------------

Install collective.fgrcon.portletadmin by adding it to your buildout::

    [buildout]

    ...

    eggs =
        collective.fgrcon.portletadmin


and then running ``bin/buildout``


Contribute
----------

- Issue Tracker: https://github.com/collective/collective.fgrcon.portletadmin/issues
- Source Code: https://github.com/collective/collective.fgrcon.portletadmin
- Documentation: https://docs.plone.org/foo/bar


Support
-------

If you are having issues, please use the issue tracker



License
-------

The project is licensed under the GPLv2.
