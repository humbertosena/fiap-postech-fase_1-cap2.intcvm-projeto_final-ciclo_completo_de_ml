from __future__ import annotations

from typing import Any

from src.serving.schemas import swagger_input_example


SWAGGER_UI_HTML = """<!DOCTYPE html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>FIAP HealthCare Plus MLOps API Docs</title>
    <link rel=\"stylesheet\" href=\"https://unpkg.com/swagger-ui-dist@5/swagger-ui.css\" />
    <style>
      body { margin: 0; background: #f5f7fa; }
      .topbar { display: none; }
    </style>
  </head>
  <body>
    <div id=\"swagger-ui\"></div>
    <script src=\"https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js\"></script>
    <script>
      window.ui = SwaggerUIBundle({
        url: '/openapi.json',
        dom_id: '#swagger-ui',
        deepLinking: true,
        displayRequestDuration: true,
        defaultModelsExpandDepth: 2,
      });
    </script>
  </body>
</html>
"""


def build_openapi_spec() -> dict[str, Any]:
    input_example = swagger_input_example()
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "FIAP HealthCare Plus MLOps API",
            "version": "1.0.0",
            "description": (
                "API local de inferencia para triagem cardiaca. "
                "A aplicacao sempre serve o ultimo modelo aprovado no registro local."
            ),
        },
        "servers": [
            {"url": "http://127.0.0.1:8000", "description": "Desenvolvimento local"}
        ],
        "tags": [
            {"name": "Serving", "description": "Health check e inferencia do modelo aprovado."}
        ],
        "paths": {
            "/health": {
                "get": {
                    "tags": ["Serving"],
                    "summary": "Verifica a disponibilidade da API e do modelo aprovado.",
                    "responses": {
                        "200": {
                            "description": "Status da API.",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/HealthResponse"},
                                    "examples": {
                                        "healthy": {
                                            "value": {
                                                "status": "ok",
                                                "model_available": True,
                                                "model_name": "logistic_regression",
                                                "model_run_id": "abc123",
                                                "model_run_label": "20260329T130143Z",
                                            }
                                        }
                                    },
                                }
                            },
                        }
                    },
                }
            },
            "/predict": {
                "post": {
                    "tags": ["Serving"],
                    "summary": "Executa inferencia usando o ultimo modelo aprovado.",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/PredictionRequest"},
                                "examples": {"default": {"value": input_example}},
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Predicao realizada com sucesso.",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/PredictionEnvelope"},
                                    "examples": {
                                        "success": {
                                            "value": {
                                                "request": input_example,
                                                "response": {
                                                    "prediction": 1,
                                                    "prediction_label": "sick",
                                                    "positive_class_probability": 0.82,
                                                    "decision_threshold": 0.35,
                                                    "model_name": "logistic_regression",
                                                    "model_run_id": "abc123",
                                                    "model_run_label": "20260329T130143Z",
                                                },
                                                "request_id": "req_123",
                                            }
                                        }
                                    },
                                }
                            },
                        },
                        "400": {
                            "description": "Payload invalido.",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                }
                            },
                        },
                        "503": {
                            "description": "Modelo aprovado indisponivel.",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                }
                            },
                        },
                    },
                }
            },
        },
        "components": {
            "schemas": {
                "PredictionInput": {
                    "type": "object",
                    "required": [
                        "age",
                        "sex",
                        "chest_pain_type",
                        "resting_blood_pressure",
                        "cholesterol",
                        "fasting_blood_sugar_gt_120",
                        "rest_ecg",
                        "max_heart_rate",
                        "exercise_induced_angina",
                        "oldpeak",
                        "slope",
                        "num_vessels",
                        "thal",
                    ],
                    "properties": {
                        "age": {"type": "number", "example": 63},
                        "sex": {
                            "type": "string",
                            "enum": ["male", "female", "fem"],
                            "example": "male",
                        },
                        "chest_pain_type": {
                            "type": "string",
                            "enum": ["typical", "atypical", "non_anginal", "asymptomatic"],
                            "example": "typical",
                        },
                        "resting_blood_pressure": {"type": "number", "example": 145},
                        "cholesterol": {"type": "number", "example": 233},
                        "fasting_blood_sugar_gt_120": {
                            "type": "string",
                            "enum": ["yes", "no", "true", "false"],
                            "example": "yes",
                        },
                        "rest_ecg": {
                            "type": "string",
                            "enum": ["normal", "abnormal", "hypertrophy"],
                            "example": "normal",
                        },
                        "max_heart_rate": {"type": "number", "example": 150},
                        "exercise_induced_angina": {
                            "type": "string",
                            "enum": ["yes", "no", "true", "false"],
                            "example": "no",
                        },
                        "oldpeak": {"type": "number", "example": 2.3},
                        "slope": {
                            "type": "string",
                            "enum": ["upsloping", "flat", "downsloping"],
                            "example": "flat",
                        },
                        "num_vessels": {
                            "type": "number",
                            "nullable": True,
                            "example": 0,
                        },
                        "thal": {
                            "type": "string",
                            "nullable": True,
                            "enum": ["normal", "fixed_defect", "reversible_defect"],
                            "example": "normal",
                        },
                    },
                },
                "PredictionRequest": {
                    "type": "object",
                    "required": ["input_data"],
                    "properties": {
                        "input_data": {"$ref": "#/components/schemas/PredictionInput"}
                    },
                },
                "PredictionResponse": {
                    "type": "object",
                    "required": [
                        "prediction",
                        "prediction_label",
                        "positive_class_probability",
                        "decision_threshold",
                        "model_name",
                        "model_run_id",
                        "model_run_label",
                    ],
                    "properties": {
                        "prediction": {"type": "integer", "enum": [0, 1]},
                        "prediction_label": {"type": "string", "enum": ["buff", "sick"]},
                        "positive_class_probability": {"type": "number", "nullable": True},
                        "decision_threshold": {"type": "number", "example": 0.35},
                        "model_name": {"type": "string", "example": "logistic_regression"},
                        "model_run_id": {"type": "string", "example": "abc123"},
                        "model_run_label": {"type": "string", "example": "20260329T130143Z"},
                    },
                },
                "PredictionEnvelope": {
                    "type": "object",
                    "required": ["request", "response", "request_id"],
                    "properties": {
                        "request": {"$ref": "#/components/schemas/PredictionRequest"},
                        "response": {"$ref": "#/components/schemas/PredictionResponse"},
                        "request_id": {"type": "string", "example": "req_123"},
                    },
                },
                "HealthResponse": {
                    "type": "object",
                    "required": [
                        "status",
                        "model_available",
                        "model_name",
                        "model_run_id",
                        "model_run_label",
                    ],
                    "properties": {
                        "status": {"type": "string", "enum": ["ok", "degraded"]},
                        "model_available": {"type": "boolean"},
                        "model_name": {"type": "string", "nullable": True},
                        "model_run_id": {"type": "string", "nullable": True},
                        "model_run_label": {"type": "string", "nullable": True},
                    },
                },
                "ErrorResponse": {
                    "type": "object",
                    "required": ["error"],
                    "properties": {
                        "error": {"type": "string"},
                    },
                },
            }
        },
    }
