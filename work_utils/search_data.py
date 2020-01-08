from jsonpath import jsonpath
from work_utils.es_client import ESClient


ES_HOSTNAME = "***"
ES_TCP_PORT = 9999
host_port = [ES_HOSTNAME + ":" + str(ES_TCP_PORT)]
index_name = "cfdata_qx_index_db"
index_type = "cf_data_type"
es_client = ESClient(host_port, index_name=index_name, index_type=index_type)


def search_result(md5_id):
    query_body = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"ws_pc_id": md5_id}},
                    {"term": {"sj_type": 63}},
                    {"term": {"sj_ztxx": 1}},
                ],
                "must_not": [],
                "should": []
            }
        },
        "from": 0,
        "size": 10,
        "sort": [],
        "aggs": {}
    }
    data = es_client.search_by_query(query_body)
    result = jsonpath(data, '$..hits.total')[0]
    if result > 0:
        return True
    else:
        return False


if __name__ == '__main__':
    pass
