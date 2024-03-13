import arcpy
import os


class Toolbox:
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Open GeoScrub"
        self.alias = "opengeoscrub"

        # List of tool classes associated with this toolbox
        self.tools = [PolygonCentroids]


class PolygonCentroids:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Polygon Centroids"
        self.description = "Derives polygon centroids and generates an output point feature class. All attributes are preserved."

    def getParameterInfo(self):
        """Define the tool parameters."""
        params = [
                    arcpy.Parameter(
                      displayName="Input Feature",
                      name="in_feature",
                      datatype="GPFeatureLayer",
                      parameterType="Required",
                      direction="Input"),
                    arcpy.Parameter(
                      displayName="Output Feature",
                      name="out_feature",
                      datatype="DEFeatureClass",
                      parameterType="Required",
                      direction="Output")
                ]
        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        input_feature_class = parameters[0].valueAsText
        output_feature_class = parameters[1].valueAsText

        out_path, out_name = os.path.split(output_feature_class)

        arcpy.AddMessage("Starting process to calculate centroid points...")

        # Assuming the spatial reference from the input feature class for the output
        spatial_ref = arcpy.Describe(input_feature_class).spatialReference
        arcpy.CreateFeatureclass_management(out_path=out_path,
                                            out_name=out_name,
                                            geometry_type="POINT",
                                            spatial_reference=spatial_ref)
        arcpy.AddMessage(f"Created new centroid feature class: {output_feature_class}")

        # Derive our fields
        arcpy.AddMessage(f"We are getting all your attributes for ya... hang on just one second...")

        exclude_fields = ["OBJECTID", "Shape"]
        fields = [field for field in arcpy.ListFields(input_feature_class) if field.name not in exclude_fields]

        
        for field in fields:
            #arcpy.AddMessage(f"Adding {field.name}...")
            arcpy.AddField_management(output_feature_class, field.name, field.type, field.precision, 
                                      field.scale, field.length, field.aliasName, field.isNullable,
                                      field.required, field.domain)

        # Copy attributes and calculate centroids
        fields_names = [field.name for field in fields]
        fields_names.append("SHAPE@XY")  # To insert the centroid geometry

        arcpy.AddMessage(f"Okay great I have em! Let's roll...")

        with arcpy.da.SearchCursor(input_feature_class, fields_names) as search_cursor, \
             arcpy.da.InsertCursor(output_feature_class, fields_names) as insert_cursor:
            for row in search_cursor:
                centroid = row[-1].centroid
                new_row = row[:-1] + (centroid.X, centroid.Y)
                insert_cursor.insertRow(new_row)

        arcpy.AddMessage("Process completed successfully! Enjoy the centroids :)")
        return True

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
