# orchestrate models add --name watsonx/openai/gpt-oss-120b --app-id watsonx_credentials
# orchestrate models add --name watsonx/meta-llama/llama-4-maverick-17b-128e-instruct-fp8 --app-id watsonx_credentials

orchestrate models import --file watsonx-model.yaml --app-id watsonx_credentials
