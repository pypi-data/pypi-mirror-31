import ee

## load stripes
def getExtractionPolygon(pathToAsset):
    return ee.FeatureCollection(str(pathToAsset))


# select and return reducer
def select_reducer(reducer):
    if reducer == 'mean':
        reducer = ee.Reducer.mean()
    elif reducer == 'median':
        reducer = ee.Reducer.median()
    elif reducer == 'mode':
        reducer = ee.Reducer.mode()
    elif reducer == 'sum':
        reducer = ee.Reducer.sum()
    elif reducer == 'min':
        reducer = ee.Reducer.min()
    elif reducer == 'max':
        reducer = ee.Reducer.max()
    else:
        print 'Parameter should be mean, median, mode or sum'
        sys.exit()
    return reducer


def select_reducer_with_outputName(reducer, productName):
    if reducer == 'mean':
        reducer = ee.Reducer.mean().setOutputs([productName])
    elif reducer == 'median':
        reducer = ee.Reducer.median().setOutputs([productName])
    elif reducer == 'mode':
        reducer = ee.Reducer.mode().setOutputs([productName])
    elif reducer == 'sum':
        reducer = ee.Reducer.sum().setOutputs([productName])
    elif reducer == 'min':
        reducer = ee.Reducer.min().setOutputs([productName])
    elif reducer == 'max':
        reducer = ee.Reducer.max().setOutputs([productName])
    else:
        print 'Parameter should be mean, median, mode or sum'
        sys.exit()
    return reducer



def filter_chirps_precipitation(yearStart, yearEnd, reducer):
    'temporal filter chirps data and aggregate to one image with one band with  the given reducer'

    #          .filterDate(ee.String(str(yearStart)).cat('-01-01'),ee.String(str(yearEnd)).cat('-12-31'))\
    reduce = select_reducer(reducer)
    chirps = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
        .filter(ee.Filter.calendarRange(int(yearStart), int(yearEnd), 'year')) \
        .reduce(reduce)\
        .rename('chirps_precipitation_mm')
    return chirps

## jrc surface water
def filter_jrc_distanceToWater(yearStart, yearEnd, reducer):
    reduce = select_reducer(reducer)
    jrc_permanentWater = ee.ImageCollection("JRC/GSW1_0/YearlyHistory")\
        .filter(ee.Filter.calendarRange(int(yearStart), int(yearEnd), 'year'))\
        .reduce(reduce)\
        .gte(1)\
        .rename('jrc_distanceToWater_km')
    return jrc_permanentWater

## modis treecover
def filter_modis_treeCover(yearStart, yearEnd, reducer):
    reduce = select_reducer(reducer)
    modis_treecover = ee.ImageCollection("MODIS/051/MOD44B") \
        .filter(ee.Filter.calendarRange(int(yearStart), int(yearEnd), 'year'))\
        .reduce(reduce) \
        .select([ee.String('Percent_Tree_Cover').cat('_').cat(ee.String(reducer))], ['modis_treeCover_percent'])
    return modis_treecover

## modis nonTreecoverVegetaiton
def filter_modis_nonTreeCoverVegetation(yearStart, yearEnd, reducer):
    reduce = select_reducer(reducer)
    modis_nonTreeCoverVegetation = ee.ImageCollection("MODIS/051/MOD44B") \
        .filter(ee.Filter.calendarRange(int(yearStart), int(yearEnd), 'year')) \
        .reduce(reduce) \
        .select([ee.String('Percent_NonTree_Vegetation').cat('_').cat(ee.String(reducer))], ['modis_nonTreeCoverVegetation_percent'])
    return modis_nonTreeCoverVegetation

# modis non Vegetation
def filter_modis_nonVegetation(yearStart, yearEnd, reducer):
    reduce = select_reducer(reducer)
    modis_nonVegetation = ee.ImageCollection("MODIS/051/MOD44B") \
        .filter(ee.Filter.calendarRange(int(yearStart), int(yearEnd), 'year')) \
        .reduce(reduce) \
        .select([ee.String('Percent_NonVegetated').cat('_').cat(ee.String(reducer))],['modis_nonVegetated_percent'])
    return modis_nonVegetation

# modis quality
def filter_modis_quality(yearStart, yearEnd, reducer):
    reduce = select_reducer(reducer)
    modis_quality = ee.ImageCollection("MODIS/051/MOD44B") \
        .filter(ee.Filter.calendarRange(int(yearStart), int(yearEnd), 'year')) \
        .reduce(reduce) \
        .select([ee.String('Quality').cat('_').cat(ee.String(reducer))], ['modis_quality'])
    return modis_quality

# srtm elevation
def filter_elevation():
    elevation = ee.Image('CGIAR/SRTM90_V4')\
        .rename('srtm_elevation_m')
    return elevation

# srtm slope
def filter_slope():
    slope = ee.Terrain.slope(ee.Image('CGIAR/SRTM90_V4'))\
        .rename('srtm_slope_degrees')
    return slope

# srtm elevation
def filter_friction():
    friction = ee.Image("Oxford/MAP/friction_surface_2015_v1_0")\
        .rename('oxford_friction_min/m')
    return friction

# srtm elevation
def filter_accessibility():
    accessibility = ee.Image("Oxford/MAP/accessibility_to_cities_2015_v1_0")\
        .rename('oxford_accessibility_min')
    return accessibility


def reduceOverRegions(image, extractionPolygon, scale, reducer, productName):
    reduce = select_reducer_with_outputName(reducer, productName)
    bandsPerFeature = image\
        .reduceRegions(extractionPolygon, reduce, ee.Number(scale))
    return bandsPerFeature



def reduceOverRegion(image, extractionPolygon, scale, reducer, productName):
    def reduceFeature(feature):
        reduce = select_reducer_with_outputName(reducer, productName)
        feature_new = feature.set(ee.Image(image).reduceRegion(reduce, feature.geometry(), ee.Number(scale),  bestEffort = True))
        return feature_new
    bandsPerFeature = extractionPolygon.map(reduceFeature)
    # select(ee.List(['system:index', 'ID']).cat(image.bandNames()), ee.List(['system:index', 'ID']).cat(image.bandNames()),False)
    return bandsPerFeature


def creatRandomPolygons(region, numPolygons):
    'to test with random polygons'
    # creat random points in given region
    points = ee.FeatureCollection.randomPoints(region, ee.Number(numPolygons))
    # function for map
    def buffer(feature):
        return feature.buffer(10000).set('ID',feature.id())
    # creat buffer
    feature_buffer = points.map(buffer)

    return feature_buffer


def exportToAsset(image, name, scale, polygon):
    image_clipped = image.clip(polygon.union())
    region = polygon.geometry().bounds().coordinates()
    task = ee.batch.Export.image.toAsset(
        image=image_clipped,
        description="example",
        assetId=str("users/JesJehle/"+name),
        region=region.getInfo(),
        scale=scale
    )

    task.start()
    return task.status()



def creatMultiBandImage(params):

    if 'srtm_slope' in params["productName"][0]:
        image = filter_slope()
        # image = image.addBands(slope)
    if 'srtm_elevation' in params["productName"][0]:
        image = filter_elevation()
        # image = image.addBands(elevation)
    if 'chirps_precipitation' in params["productName"][0]:
        image = filter_chirps_precipitation(int(params["yearStart"][0]), int(params["yearEnd"][0]),
                                            params["temporalReducer"][0])
        # image = image.addBands(chirps_precipitation)
    if 'jrc_distanceToWater' in params["productName"][0]:
        jrc_Water = filter_jrc_distanceToWater(int(params["yearStart"][0]), int(params["yearEnd"][0]),
                                               params["temporalReducer"][0])
        image = jrc_Water.fastDistanceTransform(1000).multiply(ee.Image.pixelArea()).sqrt().divide(1000)
        # image = image.addBands(jrc_distanceToWater)
    if 'modis_treeCover' in params["productName"][0]:
        image = filter_modis_treeCover(int(params["yearStart"][0]), int(params["yearEnd"][0]),
                                       params["temporalReducer"][0])
        # image = image.addBands(modis_treeCover)
    if 'modis_nonTreeVegetation' in params["productName"][0]:
        image = filter_modis_nonTreeCoverVegetation(int(params["yearStart"][0]),
                                                    int(params["yearEnd"][0]),
                                                    params["temporalReducer"][0])
        # image = image.addBands(modis_nonTreeCoverVegetation)
    if 'modis_nonVegetated' in params["productName"][0]:
        image = filter_modis_nonVegetation(int(params["yearStart"][0]), int(params["yearEnd"][0]),
                                           params["temporalReducer"][0])
        # image = image.addBands(modis_nonVegetated)
    if 'modis_quality' in params["productName"][0]:
        image = filter_modis_quality(int(params["yearStart"][0]), int(params["yearEnd"][0]),
                                     params["temporalReducer"][0])
        # image = image.addBands(modis_quality)
    if 'oxford_friction' in params["productName"][0]:
        image = filter_friction()
        # image = image.addBands(friction)
    if 'oxford_accessibility' in params["productName"][0]:
        image = filter_accessibility()
        # image = image.addBands(accessibility)

    return image.rename(str(params["productName"][0]))


def sizeTest(numPolygons):
    geometry = ee.Geometry.Polygon(
        [[[14.677734375, 3.8167549960716305],
          [16.5234375, -15.989487632061891],
          [29.8828125, -27.085206348757687],
          [35.859375, -5.645134224527403],
          [33.3984375, 14.91648401912482]]])

    polygon = creatRandomPolygons(geometry, int(numPolygons))
    return polygon


def exportTableToDrive(featureCollection, format, name, export):
    # format = CSV, GeoJSON, KML, KMZ
    task = ee.batch.Export.table.toDrive(
        collection=featureCollection,
        description=str(name),
        fileFormat = str(format),
        folder = "GEE2R_temp")

    if str(export) == str('TRUE'):
        task.start()
        status = task.status()
    else:
        status = task

    return status


def exportImageToDrive(image, scale, name):

    task = ee.batch.Export.image.toDrive(
        image=image,
        description=str(name),
        scale=int(scale))

    task.start()
    return task.status()
