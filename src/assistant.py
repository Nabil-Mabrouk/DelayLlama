from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2


class Assistant:
    def __init__(self, nlp_model):
        """
        Initialize an Assistant instance.

        Args:
            nlp_model: The natural language processing model for text-based interaction.
        """
        self.nlp_model = nlp_model

    def process_user_queries(self, user_query):
        """
        Process user queries and provide responses.

        Args:
            user_query (str): User's query.

        Returns:
            str: Assistant's response to the user's query.
        """
        response = self.nlp_model.run(user_query)
        return response

    def explain_recommendation(self, recommendation):
        """
        Explain a trading recommendation to the user.

        Args:
            recommendation (Recommendation): The trading recommendation to explain.

        Returns:
            str: Explanation of the recommendation.
        """
        response = self.nlp_model.run(recommendation)
        return response
    
    def generate_recommendation(self, recommendation):
        """
        Explain a trading recommendation to the user.

        Args:
            recommendation (Recommendation): The trading recommendation to explain.

        Returns:
            str: Explanation of the recommendation.
        """
        print(f"Recommandations: {recommendation}")
        #response = self.nlp_model.run(recommendation)
        return response


class Model():
    '''
        <s> - the beginning of the entire sequence.
        <<SYS>> - the beginning of the system message.
        <</SYS>> - the end of the system message.
        [INST] - the beginning of some instructions
        [/INST] - the end of the instructions
    '''
    def __init__(self, name):
        self.name=name
    
    def run(self, query):
        # Your PAT (Personal Access Token) can be found in the portal under Authentification
        PAT = '331ec2dac4f74cbca3a930ff13ffe4d7'
        # Specify the correct user_id/app_id pairings
        # Since you're making inferences outside your app's scope
        USER_ID = 'meta'
        APP_ID = 'Llama-2'
        # Change these to whatever model and text URL you want to use
        MODEL_ID = 'llama2-70b-chat'
        MODEL_VERSION_ID = '6c27e86364ba461d98de95cddc559cb3'


        channel = ClarifaiChannel.get_grpc_channel()
        stub = service_pb2_grpc.V2Stub(channel)

        metadata = (('authorization', 'Key ' + PAT),)

        userDataObject = resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID)

        post_model_outputs_response = stub.PostModelOutputs(
            service_pb2.PostModelOutputsRequest(
                user_app_id=userDataObject,  # The userDataObject is created in the overview and is required when using a PAT
                model_id=MODEL_ID,
                version_id=MODEL_VERSION_ID,  # This is optional. Defaults to the latest model version
                inputs=[
                    resources_pb2.Input(
                        data=resources_pb2.Data(
                            text=resources_pb2.Text(
                                raw=query
                            )
                        )
                    )
                ]
            ),
            metadata=metadata
        )
        if post_model_outputs_response.status.code != status_code_pb2.SUCCESS:
            print(post_model_outputs_response.status)
            raise Exception(f"Post model outputs failed, status: {post_model_outputs_response.status.description}")

        # Since we have one input, one output will exist here
        output = post_model_outputs_response.outputs[0]
        return output.data.text.raw