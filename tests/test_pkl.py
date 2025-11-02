import joblib
model_obj = joblib.load("/Users/minhtan/Documents/GitHub/Final_RS/models/minilm_recommender_light.pkl")
print(type(model_obj))
if (
        isinstance(model_obj, dict)):
    print("Keys:", model_obj.keys())