cmake_minimum_required(VERSION 3.4)
project(IndiaCenterOfMass LANGUAGES)

file(GLOB SRTM_ZIP_FILES ${CMAKE_CURRENT_SOURCE_DIR}/srtm_raw_data/*.zip)

# Run geojson to ESRI shape file. We'll need it later to cut the raster.
set(INDIA_GEOJSON ${CMAKE_CURRENT_SOURCE_DIR}/india-composite.geojson)
set(INDIA_ESRI ${CMAKE_BINARY_DIR}/india.shp)
add_custom_target(geojson2shp ALL DEPENDS ${INDIA_ESRI})
add_custom_command(OUTPUT ${INDIA_ESRI}
  DEPENDS ${INDIA_GEOJSON}
  COMMAND ogr2ogr -f "ESRI Shapefile" ${INDIA_ESRI} "${INDIA_GEOJSON}"
  COMMENT "GeoJSON to ESRI shape file"
  VERBATIM)

# Download all zip files.
add_custom_target(zip2tiff)
set(GEO_TIFF_FILES "")
foreach(_zipfile IN ITEMS ${SRTM_ZIP_FILES})
  get_filename_component(_zipfilename ${_zipfile} NAME_WE)
  set(_tiffile ${CMAKE_BINARY_DIR}/${_zipfilename}.tif)
  message(STATUS "Converting zipfile to tiffile ${_zipfile}")
  set(_tgtname ${_zipfilename}2tiff)
  add_custom_target(${_tgtname} DEPENDS ${_tiffile})
  add_custom_command(OUTPUT ${_tiffile}
    COMMAND unzip -o ${_zipfile}
    COMMENT "Converting zip to tif"
    VERBATIM)
  add_dependencies(zip2tiff ${_tgtname})
  list(APPEND GEO_TIFF_FILES ${_tiffile})
endforeach()

# Now stitch all tif together.
set(MERGED_TIF_FILE ${CMAKE_BINARY_DIR}/india.tif)
set(MERGED_PNG_FILE ${CMAKE_BINARY_DIR}/india.png)

add_custom_target(stitch DEPENDS ${MERGED_TIF_FILE})
add_custom_command(OUTPUT ${MERGED_TIF_FILE}
  DEPENDS zip2tiff
  COMMAND gdal_merge.py ${GEO_TIFF_FILES} -o ${MERGED_TIF_FILE}
  COMMENT "Stiching TIF files together ${MERGED_TIF_FILE}" 
  WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
  VERBATIM)

# now india geotiff file to a png; this one is for displaying.
add_custom_target(summary ALL DEPENDS ${MERGED_PNG_FILE})
add_custom_command(OUTPUT ${MERGED_PNG_FILE}
  DEPENDS stitch
  COMMAND gdal_translate -of PNG -ot UInt16 -outsize 10% 10%
    ${MERGED_TIF_FILE}
    ${MERGED_PNG_FILE}
  COMMENT "Converting TIF to PNG"
  WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
  VERBATIM)

# Now cutting the boundary using shapefile.
set(CLIPPED_RASTER ${CMAKE_BINARY_DIR}/india.clipped.tif)
add_custom_target(clip_raster DEPENDS ${CLIPPED_RASTER})
add_custom_command(OUTPUT ${CLIPPED_RASTER}
  DEPENDS stitch
  COMMAND gdalwarp -cutline ${INDIA_ESRI} -crop_to_cutline 
    ${MERGED_TIF_FILE} ${CLIPPED_RASTER}
  COMMENT "Clipping raster using shape file"
  VERBATIM)
add_custom_command(TARGET clip_raster POST_BUILD
  COMMAND gdal_translate -of PNG -ot UInt16 -outsize 10% 10%
    ${CLIPPED_RASTER} india.clipped.png
  COMMENT "Converting clipped raster to PNG file"
  VERBATIM)

# Now generate the grid data in XYZ format. This step will create roughly 30GB
# worth of file. Beware!
set(GRID_FILE ${CMAKE_BINARY_DIR}/india.clipped.csv)
add_custom_target(grid_data ALL DEPENDS ${GRID_FILE})
add_custom_command(OUTPUT ${GRID_FILE} DEPENDS clip_raster
  COMMAND gdal_translate -of XYZ ${CLIPPED_RASTER} ${GRID_FILE}
  COMMENT "Raster to XYZ grid file."
  VERBATIM)

# now compute the center of mass. An awk script would do the job.
add_custom_command(TARGET grid_data POST_BUILD
  COMMAND gawk -M -v PREC=100 
    "{w1=w1+$3; w2=w2+$3; e1=e1+$2*$3; e2=e2+$1*$3;} END {print e1/w1 e2/w2}"
    ${GRID_FILE}
  COMMENT "Computing center of mass using gawk"
  VERBATIM)

