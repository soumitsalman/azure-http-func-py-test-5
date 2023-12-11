import json
import random
import azure.functions as func
import logging

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="find_contents")
@app.function_name(name="find_contents")
@app.queue_output(arg_name="usrquery", queue_name="filter-queue", connection="AzureWebJobsStorage")
def find_contents(req: func.HttpRequest, usrquery: func.Out[func.QueueMessage]) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    query = req.params.get('query')
    if not query:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            query = req_body.get('query')

    if query:
        query_emb = "EMB_" + query
        usrquery.set(_to_json_str(random.randint(1, 100), query_emb))
        return func.HttpResponse(f"Hello, {query_emb}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a query in the query string or in the request body for a personalized response.",
             status_code=200
        )
    
@app.function_name("create_embeddings")
@app.queue_trigger(arg_name="inmsg", queue_name="filter-queue", connection="AzureWebJobsStorage")
@app.queue_output(arg_name="outmsg", queue_name="embedding-queue", connection="AzureWebJobsStorage")
def create_embedding(inmsg: func.QueueMessage, 
                     outmsg: func.Out[func.QueueMessage]):
    ct = inmsg.get_json()
    logging.info(f"create embedding function triggered for {ct['id']}\n")    
    ot = _to_json_str(ct['id'], [random.randint(1, len(ct['content'])) for i in range(5)])
    outmsg.set(ot)


def _to_json_str(id, content) -> str:
    return json.dumps({'id': id, 'content': content}, indent=2)