import json

from src.models.train import train_model


def evaluate_pipeline() -> dict[str, object]:
    result = train_model(log_to_mlflow=False)
    return {
        "status": "evaluated",
        "model_name": result["model_name"],
        "metrics": result["metrics"],
        "fairness": result["fairness"],
        "artifacts": result["artifacts"],
    }



def main() -> None:
    print(json.dumps(evaluate_pipeline(), indent=2))


if __name__ == "__main__":
    main()
