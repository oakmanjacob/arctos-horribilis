SELECT *
FROM
  (SELECT flat.guid,
          flat.subspecies,
          CAST(flat.cat_num AS INTEGER) AS catalognumberint,
          flat.collectors,
          state_prov,
          county,
          flat.spec_locality,
          collectornumber,
          began_date,
          ended_date,
          parts,
          sex,
          dec_lat,
          dec_long,
          coordinateuncertaintyinmeters,
          a0.attribute_value AS "total length",
          a1.attribute_value AS "tail length",
          a2.attribute_value AS "hind foot with claw",
          a3.attribute_value AS "ear from notch",
          a4.attribute_value AS "ear from crown",
          a5.attribute_value AS "weight",
          a0.attribute_units AS "total length unit",
          a1.attribute_units AS "tail length unit",
          a2.attribute_units AS "hind foot with claw unit",
          a3.attribute_units AS "ear from notch unit",
          a4.attribute_units AS "ear from crown unit",
          a5.attribute_units AS "weight unit",
          a6.attribute_value AS "reproductive data",
          a7.attribute_value AS "unformatted measurements"
   FROM flat
   LEFT OUTER JOIN
     (SELECT *
      FROM attributes
      WHERE attribute_type = 'total length') AS a0 ON flat.collection_object_id = a0.collection_object_id
   LEFT OUTER JOIN
     (SELECT *
      FROM attributes
      WHERE attribute_type = 'tail length') AS a1 ON flat.collection_object_id = a1.collection_object_id
   LEFT OUTER JOIN
     (SELECT *
      FROM attributes
      WHERE attribute_type = 'hind foot with claw') AS a2 ON flat.collection_object_id = a2.collection_object_id
   LEFT OUTER JOIN
     (SELECT *
      FROM attributes
      WHERE attribute_type = 'ear from notch') AS a3 ON flat.collection_object_id = a3.collection_object_id
   LEFT OUTER JOIN
     (SELECT *
      FROM attributes
      WHERE attribute_type = 'ear from crown') AS a4 ON flat.collection_object_id = a4.collection_object_id
   LEFT OUTER JOIN
     (SELECT *
      FROM attributes
      WHERE attribute_type = 'weight') AS a5 ON flat.collection_object_id = a5.collection_object_id
   LEFT OUTER JOIN
     (SELECT *
      FROM attributes
      WHERE attribute_type = 'reproductive data') AS a6 ON flat.collection_object_id = a6.collection_object_id
   LEFT OUTER JOIN
     (SELECT *
      FROM attributes
      WHERE attribute_type = 'unformatted measurements') AS a7 ON flat.collection_object_id = a7.collection_object_id
   WHERE guid_prefix LIKE 'MVZ:Mamm'
     AND species LIKE 'Sorex vagrans'
     AND country IN ('United States',
                     'Mexico',
                     'Canada',
                     'NULL')
     AND state_prov IN ('Alaska',
                        'Alberta',
                        'Arizona',
                        'Arkansas',
                        'British Columbia',
                        'California',
                        'Colorado',
                        'Idaho',
                        'Illinois',
                        'Kansas',
                        'Mexico',
                        'Michigan',
                        'Montana',
                        'Nebraska',
                        'New Mexico',
                        'North Dakota',
                        'Nevada',
                        'Oregon',
                        'Saskatchewan',
                        'South Dakota',
                        'Texas',
                        'Utah',
                        'Washington',
                        'Wyoming',
                        'Aguascalientes',
                        'Baja California',
                        'Baja California Sur',
                        'Campeche',
                        'Chiapas',
                        'Chihuahua',
                        'Coahuila',
                        'Colima',
                        'Durango',
                        'Guanajuato',
                        'Guerrero',
                        'Hidalgo',
                        'Jalisco',
                        'México',
                        'Mexico',
                        'México City',
                        'Mexico City',
                        'Michoacán',
                        'Michoacan',
                        'Morelos',
                        'Nayarit',
                        'Nuevo León',
                        'Nuevo Leon',
                        'Oaxaca',
                        'Puebla',
                        'Querétaro',
                        'Queretaro',
                        'Quintana Roo',
                        'Sinaloa',
                        'Sonora',
                        'San Luis Potosi',
                        'Tamaulipas',
                        'Tlaxcala',
                        'Veracruz',
                        'Yucatán',
                        'Yucatan',
                        'Zacatecas')) AS specimen_data