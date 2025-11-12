# LAB 2: AI Gateway


1. create `.env` file in the folder of the model source you want to add. (/watsonx, /groq or /gemini)
2. Paste the content from the `env-tamplete` file, and fill in with required keys (for watsonx keys, please see instruction on how to get wxai key from README in watsonx folder)

### Adding model to watsonx.Orchestrate instance
3. run the following command in folder. 

if you have not setup orchestrate environment, run
```
orchestrate env add -n stgb-inox -u <your-WO_URL>
```
then activate the environment by run
```
orchestrate env activate stgb-inox
```
After run the second command, you will be prompt to input your `WATSONX_API_KEY` you obtain earlier.

After that, run command below to setup model connection


```
bash setup_connection.sh
```
Then, run the following command to add model
```
bash add_model.sh
```
10. the model should now show uo on your instance
![alt text](images/image-5.png)

