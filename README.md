
**Still labeled experimetal, has some issues. Can overwrite your QGIS-Project**

# Label importer

This Plugin assists in importing label placement data from an auxiliary layer in another project. It focuses exclusively on label-related fields, disregarding non-label-related fields in the source project's auxiliary layer. Additionally, it operates independently without requiring any other plugins.

## Workflow

select...
- ... the layer in the currently opened project (target layer)
- ... the id/primary-key field for the target layer --> this field will be used for the auxiliary layer
- ... the project you want to import the label placement settings from (source project)
- ... the layer in the source project you want to import the label placement settings from
- ... wheter you want to import the symbology of the source layer as well

## Important to know

- only auxiliary fields with label informations will be imported.
- During the process, the system does not verify if the source project was saved using an older QGIS version. Therefore, I advise ensuring that the source project is stored in the same version you are using to import the label data.
- The plugin is marked as experimental and has not undergone extensive testing yet.
