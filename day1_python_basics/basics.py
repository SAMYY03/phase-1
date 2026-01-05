name : str = "samy" 
age : int = 25
is_ai_student : bool = True
print("name:", name)
print("age:", age)
print("ai student:", is_ai_student)  
skills : list[str]= ["python","ai","fastapi"]
print(skills[0])
skills.append("machine learning")
for skill in skills:
   print("learning:", skill)
print(len(skills))


# Dictionary practice//////////////////////


llm_info : dict[str,str]= {
   "name" : "LLaMa",
   "type" : "Local llm",
   "use_case" : "RAG"
}
llm_info["version"] = "3.1"
for key, value in llm_info.items():
   print(key ,"->",value )


   # Conditions practice/////////////////////

   ai_level : "str"="beginner"
   if ai_level == "beginner" :
      print("focus on python and basics")
   elif ai_level == "intermediate":
      print("focus on RAG and fastAPI")
   else :
      print("focus on multi-agent systems")   


# Loop practice///////////////////

documents = [
    "AI improves productivity.",
    "Python is great for AI.",
    "RAG reduces hallucinations."
]
for doc in documents:
 print("document:", doc)

      