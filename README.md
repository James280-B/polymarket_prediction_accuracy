# polymarket_prediction_accuracy
Python code to search through polymarket data api via selected tags and find the average prediction accuracy of markets in a given time horizon.


## MAIN WORKFLOW OUTLINE
Contains three input variables being number of markets, horizon for prediction and specific labels for which markets
to compute the average for. Note current code does to support "classic" labels, eg these labels must be found from 
running the generate tag list function. Tag sorting / label sorting will be added later.

## TODO
- add error handling classes
- complete tag sorting
- decrease code run time / general improvements