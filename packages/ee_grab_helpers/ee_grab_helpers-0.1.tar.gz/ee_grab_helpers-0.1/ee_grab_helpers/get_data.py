import sys
import ee
from pandas import read_csv as read
#import pandas.read_csv as read_csv
import final
import json





# load system params from R
params = read("params.csv", delimiter=',')
# print(params)


ee.Initialize()

# import polygons
#polygon = final.getExtractionPolygon(pathToAsset= params["assetPath"][0])
polygon = ee.FeatureCollection(ee.String(params["ft_id"][0]))
# combine all selected images into a multiband image
environmental_variable = final.creatMultiBandImage(params=params)



# reduce multiband image with given reducer over polygon
# featureClass = final.reduceOverRegions(multiBandImage=environmental_variable, extractionPolygon=polygon, scale=int(params["resolution"][0]), reducer=params["spatialReducer"][0])
featureClass = final.reduceOverRegions(image=environmental_variable, extractionPolygon=polygon, scale=int(params["resolution"][0]), reducer=params["spatialReducer"][0], productName=params["productName"][0])

# projection = featureClass.getInfo()
# print(projection)
# define filter


# export feature collection to drive
status = final.exportTableToDrive(featureClass, params["outputFormat"][0], params["productName"][0], "TRUE")

jsonData = json.dumps(status)

with open('exportInfo.json', 'w') as f:
    json.dump(jsonData, f)






#projection = featureClass.geometry().projection().getInfo()



# print status









#if 'jrc_distanceToWater' in params:
#    jrc_distanceToWater = final.filter_jrc_distanceToWater(params["year_start"][0], params["year_end"][0], params["jrc_distanceToWater"][0])
#    euclidean =  ee.Kernel.euclidean(100)
#    distance = jrc_distanceToWater\
#        .distance(euclidean, False)
#    featureClassDistance = final.reduceOverRegion(image=distance, extractionPolygon=polygon, scale=1000, reducer=params["spatialReducer"][0])
#    filter = ee.Filter.equals(
#        leftField = 'system:index',
#        rightField = 'system:index')
#    # define the join.#
#
#    innerJoin = ee.Join.inner()
#    joined = innerJoin.apply(featureClass, featureClassDistance,  filter)
#    # map over feature to extract and reformat properties
#    def catProperties(pair):
#        f1 = ee.Feature(pair.get('primary'))
#        f2 = ee.Feature(pair.get('secondary'))
#        return f1.set(f2.toDictionary())#
#
#    featureClass = joined.map(catProperties)
