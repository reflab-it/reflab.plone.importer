# reflab.plone.importer
A procedure and a collection of utils for importing contents in Plone

## Vision

- Manage in an simple way the common tasks related to the import of contents in Plone (eg: for a migration)
- Data source format is a convention and the tool should not provide any feature to manage different organizations (that in case should be provided via an external converter)
- All tasks included in this package are performed by just using plone.api; any other logic should be provided via external "subtask plugin"

## Data structure
Since Plone / Zope database is organized as a filesystem (directory and files), the idea is to map the same organization on the source in the OS filesystem.

## Configurations and running
All the configurations should be managed in a cfg file; the default location of this file is in the same directory where the importer is executed.

To execute the importer a new instance command is available; so from a typical buildout structure this can be done by executing

```
$./bin/instance import path/to/importer.cfg
```

### Conventions
- The root of the source must contain a set of directories, one for each content to be created in a destination container of Plone
- The name of the directory will be the id of the object in Plone
- Each subdirectory (in a recursive way) will be an object contained in the parent "folderish" object
- All attributes of the Plone objectes are stored in the data source inside a file named "data.json" of each directory
- Attributes stored as blobs (eg: file and images) are placed in a subdirectory named with the convention `_` + `attributename` (eg: `_attachment`); the file inside this directory will be imported with the filename found
- The data.json file should contain:
    - A `fields` key containng an object with a key for each attribute to be imported
    - each attribute must have a `value` and `type` key
    - a `portal_type` key matching an available content type in Plone
    - a `review_state` key matching an available state of the workflow associated to the portal type

### Example of source data on filesystem

```
export-root
    folder-1
        data.json
    folder-2
        document-1
            data.json
            _image
                cover.png
        folder-2-1
            data.son
```

### Example of data.json
```
{
    "fields": {
        "title": {
            "type": "string",
            "value": "Folder Title"
        }
    },
    "portal_type": "Folder",
    "review_state: "published"
}
```

## Data type
A set of default data type mapping for converting the string presentation of the value is provided.

This can be replaced using an option in the importer.cfg 

## Subtasks
It is common that after an import a set of additional task should be performed; these can be defined in the importer.cfg file


## TODO
- management of UIDS
- management of workflow state
- management of local roles
- management of Attribtute annotations



