SELECT
count(*) as specimen_count, species, county
FROM
flat
WHERE
guid_prefix ~ '^MVZ'
AND
species in ('Myotis occultus', 'Eptesicus fuscus', 'Nyctinomops macrotis', 'Macrotus californicus', 'Myotis californicus', 'Parastrellus hesperus', 'Myotis melanorhinus', 
'Myotis thysanodes', 'Eumops perotis', 'Myotis lucifugus', 'Myotis evotis', 'Myotis volans', 'Tadarida brasiliensis', 'Choeronycteris mexicana', 'Nyctinomops femorosaccus', 
'Lasionycteris noctivagans', 'Euderma maculatum', 'Corynorhinus townsendii', 'Lasiurus xanthinus', 'Myotis yumanensis', 'Antrozous pallidus', 'Lasiurus frantzii', 'Lasiurus blossevillii', 
'Lasiurus cinereus', 'Myotis ciliolabrum')
AND
state_prov ~ 'California'
AND
(parts LIKE '%skin%' OR parts LIKE '%whole organism%')
GROUP BY species, county