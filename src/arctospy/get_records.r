if(!require("ArctosR")){
    install.packages("remotes", repos = "http://cran.us.r-project.org")
    remotes::install_github("hrhwilliams/ArctosR")
    library("ArctosR")
}

args <- commandArgs(TRUE)

response <- get_records(
  scientific_name = args, guid_prefix = "MVZ:Mamm",
  columns = list("collection_object_id","guid", "scientific_name","ended_date","collectors","collector_number","preparators","creator","total_length","tail_length","hind_foot_with_claw","ear_from_notch","ear_from_crown","weight","reproductive_data"),
  limit = 5000,
  all_records = TRUE
)

file_name = paste(uuid::UUIDgenerate(), ".csv")
save_response_csv(response, file_name, with_metadata = FALSE)
write(file_name, stdout())