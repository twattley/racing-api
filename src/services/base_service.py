import pandas as pd
class BaseService:
    def __init__(self):
        pass

    def data_to_dict(self, data: pd.DataFrame) -> list[dict]:
        return [{k: v if pd.notna(v) else None for k, v in d.items()} for d in data.to_dict(orient='records')]
    
    def format_todays_races(self, data: pd.DataFrame) -> list[dict]:
        data = data.assign(race_class=data['race_class'].fillna(0).astype(int).replace(0, None))
        grouped = data.groupby('course_id')
        courses = []

        for course_id, group in grouped:
            races = group.to_dict(orient='records')
            course_info = {
                'course': group['course'].iloc[0],
                'course_id': course_id,
                'races': races
            }
            courses.append(course_info)

        return [{
            'race_date': data['race_date'].iloc[0],
            'courses': courses,
        }]
    
    def convert_string_columns(self, data: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
        for column in columns:
            data[column] = data[column].astype(str)
        return data
    
    def convert_integer_columns(self, data: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
        for column in columns:
            data[column] = data[column].astype("Int64")
        return data
