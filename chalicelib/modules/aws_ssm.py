import boto3


class AWS_SSM:
    def __init__(self):
        self.client = boto3.client("ssm")

    def get_parameter_value(self, name: str, with_decryption: bool = True):
        """
        Retrieves the value of a parameter from the AWS Systems Manager (SSM) Parameter Store.

        Args:
            name (str): The name of the parameter to retrieve.
            with_decryption (bool, optional): Whether to decrypt the parameter value if it is encrypted. Defaults to True.

        Returns:
            str: The value of the parameter.

        Raises:
            KeyError: If the parameter is not found in the Parameter Store.

        """
        return self.client.get_parameter(Name=name, WithDecryption=with_decryption)[
            "Parameter"
        ]["Value"]

aws_ssm = AWS_SSM()