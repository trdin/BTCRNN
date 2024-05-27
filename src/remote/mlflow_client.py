import mlflow
from mlflow.onnx import load_model as load_onnx
import onnx

def download_model_onnx(mode, stage):
    model_name = f"model={mode}"

    try:
        client = mlflow.MlflowClient()
        model = load_onnx( client.get_latest_versions(name=model_name, stages=[stage])[0].source)

        onnx.save_model(model, f"./models/{mode}/model_{stage}.onnx")

        return f"./models/{mode}/model_{stage}.onnx"
    except IndexError:
        print(f"Error downloading {stage}, {model_name}")
        return None
    
def download_model(mode, stage):
    model_name = f"model={mode}"

    try:
        client = mlflow.MlflowClient()
        model = mlflow.sklearn.load_model( client.get_latest_versions(name=model_name, stages=[stage])[0].source)

        return model
    except IndexError:
        print(f"Error downloading {stage}, {model_name}")
        return None
    
def download_scaler(mode, scaler_type, stage):
    scaler_name = f"{scaler_type}={mode}"

    try:
        client = mlflow.MlflowClient()
        scaler = mlflow.sklearn.load_model(client.get_latest_versions(name=scaler_name, stages=[stage])[0].source)
        return scaler
    except IndexError:
        print(f"Error downloading {stage}, {scaler_name}")
        return None
    

def mlflow_save_scaler(client, scaler_type, scaler, mode):
    metadata = {
        "mode_name": mode,
        "scaler_type": scaler_type,
        "expected_features": scaler.n_features_in_,
        "feature_range": scaler.feature_range,
    }

    scaler = mlflow.sklearn.log_model(
        sk_model=scaler,
        artifact_path=f"models/{mode}/{scaler_type}",
        registered_model_name=f"{scaler_type}={mode}",
        metadata=metadata,
    )

    scaler_version = client.create_model_version(
        name=f"{scaler_type}={mode}",
        source=scaler.model_uri,
        run_id=scaler.run_id
    )

    client.transition_model_version_stage(
        name=f"{scaler_type}={mode}",
        version=scaler_version.version,
        stage="staging",
    )

def mlflow_save_model(model, mode, client):
    metadata = {
        "mode_name": mode,
        "model_type": "LSTM",
        "input_shape": model.input_shape,
        "output_shape": model.output_shape,
    }

    station_model = mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path=f"models/{mode}/model",
            registered_model_name=f"model={mode}",
            metadata=metadata
        )
    
    model_version = client.create_model_version(
            name=f"model={mode}",
            source=station_model.model_uri,
            run_id=station_model.run_id
        )

    client.transition_model_version_stage(
        name=f"model={mode}",
        version=model_version.version,
        stage="staging",
    )


def save_pipline(pipeline, mode, client= mlflow.MlflowClient()):
    metadata = {
        "station_name": mode,
    }

    pipeline = mlflow.sklearn.log_model(
            sk_model=pipeline,
            artifact_path=f"models/{mode}/pipeline",
            registered_model_name=f"pipeline={mode}",
            metadata=metadata
        )
    
    model_version = client.create_model_version(
            name=f"pipeline={mode}",
            source=pipeline.model_uri,
            run_id=pipeline.run_id
        )

    client.transition_model_version_stage(
        name=f"pipeline={mode}",
        version=model_version.version,
        stage="staging",
    )

def download_pipeline(mode, stage):
    model_name = f"pipeline={mode}"

    try:
        client = mlflow.MlflowClient()
        pipeline = mlflow.sklearn.load_model( client.get_latest_versions(name=model_name, stages=[stage])[0].source)

        return pipeline
    except IndexError:
        print(f"Error downloading {stage}, {model_name}")
        return None
    
def download_scaler(mode, scaler_type, stage):
    scaler_name = f"{scaler_type}={mode}"

    try:
        client = mlflow.MlflowClient()
        scaler = mlflow.sklearn.load_model(client.get_latest_versions(name=scaler_name, stages=[stage])[0].source)
        return scaler
    except IndexError:
        print(f"Error downloading {stage}, {scaler_name}")
        return None

def prod_model_save(mode):

    try:
        client = mlflow.MlflowClient()

        model_version = client.get_latest_versions(name= f"model={mode}", stages=["staging"])[0].version
        client.transition_model_version_stage(f"model={mode}", model_version, "production")

        btc_scaler_version = client.get_latest_versions(name=f"btc_scaler={mode}", stages=["staging"])[0].version
        client.transition_model_version_stage(f"btc_scaler={mode}", btc_scaler_version, "production")


        pipeline= client.get_latest_versions(name=f"pipeline={mode}", stages=["staging"])[0].version
        client.transition_model_version_stage(f"pipeline={mode}", pipeline, "production")
        
        """ other_scaler_version = client.get_latest_versions(name= f"other_scaler={mode}", stages=["staging"])[0].version
        client.transition_model_version_stage(f"other_scaler={mode}", other_scaler_version, "production") """


    except IndexError:
        print(f"#####error##### \n replace_prod_model {mode}")
        return