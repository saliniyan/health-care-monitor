from flask import Flask, render_template, request, jsonify, redirect, url_for
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import *
from sklearn.naive_bayes import GaussianNB
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.ensemble import *
import numpy as np
from plyer import notification
from threading import Thread
import time
from datetime import datetime
import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# Load and preprocess the dataset
df1 = pd.read_csv(r"C:\Users\DELL\Downloads\data (5).csv")
le = LabelEncoder()
for i in df1.columns:
    df1[i] = le.fit_transform(df1[i])

# Prepare data for modeling
X = df1.drop('Disease', axis=1)
y = df1['Disease']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Standardize features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Create an ensemble using VotingClassifier
ensemble_classifier = VotingClassifier(estimators=[
    ('knn', KNeighborsClassifier(n_neighbors=3)),
    ('rf', RandomForestClassifier()),
    ('nb', GaussianNB()),
    ('svm', SVC(probability=True))
], voting='soft')  # Experiment with 'hard' or 'soft' voting

# Train the ensemble classifier
ensemble_classifier.fit(X_train, y_train)

all_symptoms = [
    "itching", "weight_loss", "dark_urine", "excessive_hunger", "sweating", "loss_of_appetite", "skin_rash",
    "headache", "stomach_pain", "ulcers_on_tongue", "dehydration", "family_history", "mucoid_sputum",
    "extra_marital_contacts", "unsteadiness", "mood_swings", "malaise", "back_pain", "swelling_joints",
    "knee_pain", "indigestion", "pain_during_bowel_movements", "toxic_look_(typhos)", "throat_irritation",
    "shivering", "fatigue", "Unnamed: 26", "chills", "dizziness", "increased_appetite", "enlarged_thyroid",
    "yellowing_of_eyes", "puffy_face_and_eyes", "diarrhoea", "constipation", "internal_itching", "hip_joint_pain",
    "burning_micturition", "breathlessness", "redness_of_eyes", "mild_fever", "drying_and_tingling_lips",
    "irregular_sugar_level", "cold_hands_and_feets", "continuous_sneezing", "neck_pain", "passage_of_gases",
    "nausea", "sinus_pressure", "belly_pain", "weakness_of_one_body_side", "painful_walking", "spotting_ urination",
    "joint_pain", "muscle_weakness", "polyuria", "watering_from_eyes", "restlessness", "slurred_speech",
    "irritation_in_anus", "yellowish_skin", "bloody_stool", "pain_behind_the_eyes", "dischromic _patches",
    "swollen_extremeties", "abdominal_pain", "pain_in_anal_region", "loss_of_smell", "phlegm", "vomiting",
    "sunken_eyes", "blurred_and_distorted_vision", "acidity", "weakness_in_limbs", "anxiety", "muscle_pain",
    "red_spots_over_body", "congestion", "lethargy", "muscle_wasting", "obesity", "visual_disturbances",
    "brittle_nails", "spinning_movements", "high_fever", "lack_of_concentration", "chest_pain", "cough",
    "altered_sensorium", "irritability", "abnormal_menstruation", "depression", "patches_in_throat", "stiff_neck",
    "loss_of_balance", "swelled_lymph_nodes", "palpitations", "fast_heart_rate", "weight_gain", "runny_nose",
    "nodal_skin_eruptions", "blood_in_sputum"
]

# Define dictionary for storing home remedy information
home_remedies ={'Fungal infection': ['Tea Tree Oil: Tea tree oil has antifungal properties and can be diluted with a carrier oil (such as coconut oil) and applied to the affected area.\n\nGarlic: Garlic contains allicin, a compound with antifungal properties. You can crush a clove of garlic and apply it directly to the affected area.\n\nApple Cider Vinegar: Apple cider vinegar has antifungal properties. You can mix it with water and apply it to the affected area, or add it to your bathwater for a foot soak.\n\nYogurt: Yogurt contains probiotics that may help restore the balance of good bacteria on the skin or in the body. Apply plain, unsweetened yogurt to the affected area.\n\nCoconut Oil: Coconut oil has antifungal properties and can be applied directly to the affected area.\n\nOregano Oil: Oregano oil contains thymol and carvacrol, compounds with antifungal properties. Dilute oregano oil with a carrier oil and apply it to the affected area.\n\nAloe Vera: Aloe vera has soothing properties and may help relieve symptoms of fungal infections. Apply pure aloe vera gel to the affected area.\n\nProper Hygiene: Keep the affected area clean and dry, as fungi thrive in warm, moist environments. Change clothes and socks regularly, and avoid sharing personal items like towels and socks.\n\nProper Diet: Some evidence suggests that a diet rich in probiotics and low in sugar may help prevent fungal infections.\n\nTurmeric: Turmeric has antifungal and anti-inflammatory properties. You can mix turmeric powder with water to form a paste and apply it to the affected area.'], 'Allergy': ["Local Honey: Consuming local honey may help desensitize your body to pollen allergies over time. Be sure to choose honey produced in your area and consume a small amount daily.\n\nSaline Nasal Rinse: Using a saline nasal rinse or neti pot can help flush out allergens and mucus from your nasal passages, reducing congestion and irritation.\n\nSteam Inhalation: Inhaling steam from a bowl of hot water can help relieve nasal congestion and soothe irritated sinuses. You can add a few drops of essential oils like eucalyptus or peppermint for added relief.\n\nQuercetin: Quercetin is a natural antihistamine found in certain foods like onions, apples, and berries. Consuming these foods or taking quercetin supplements may help reduce allergy symptoms.\n\nProbiotics: Probiotics, found in foods like yogurt, kefir, and sauerkraut, may help support immune function and reduce allergic reactions.\n\nLocal Pollen Avoidance: Pay attention to local pollen forecasts and try to limit your outdoor activities during high pollen days. Keep windows closed and use air purifiers with HEPA filters indoors to reduce pollen exposure.\n\nTurmeric: Turmeric contains curcumin, which has anti-inflammatory properties and may help alleviate allergy symptoms. You can incorporate turmeric into your diet or take turmeric supplements.\n\nEucalyptus Oil: Eucalyptus oil has decongestant properties and can help open up your airways. You can inhale eucalyptus oil by adding a few drops to hot water or using a diffuser.\n\nAcupuncture: Some people find relief from allergy symptoms through acupuncture, which may help balance the body's energy and reduce inflammation.\n\nClean Environment: Keep your living space clean and free of dust, pet dander, and mold, as these allergens can exacerbate symptoms. Regularly vacuum carpets, wash bedding in hot water, and use dust mite covers on pillows and mattresses."], 'GERD': ["Dietary Changes:\n\nAvoid trigger foods that can exacerbate GERD symptoms, such as spicy, acidic, fatty, and fried foods.\nEat smaller, more frequent meals instead of large meals, and avoid eating late at night or before lying down.\nIncrease your intake of fiber-rich foods like fruits, vegetables, and whole grains, which can help promote digestion and reduce symptoms.\nLifestyle Modifications:\n\nMaintain a healthy weight, as excess weight can put pressure on the abdomen and worsen GERD symptoms.\nElevate the head of your bed by 6 to 8 inches to prevent stomach acid from refluxing into the esophagus while you sleep.\nAvoid tight clothing that puts pressure on your abdomen, which can increase reflux.\nHerbal Remedies:\n\nChamomile tea: Chamomile has anti-inflammatory properties and may help soothe the digestive tract. Drink chamomile tea between meals to help relieve symptoms.\nGinger: Ginger has natural anti-inflammatory properties and may help reduce symptoms of GERD. You can consume ginger tea or add fresh ginger to your meals.\nApple Cider Vinegar:\n\nAlthough acidic in nature, some people find relief from GERD symptoms by diluting a tablespoon of apple cider vinegar in a glass of water and drinking it before meals. However, this remedy may not work for everyone, so it's essential to monitor your symptoms.\nAloe Vera:\n\nAloe vera juice may help soothe inflammation in the esophagus and alleviate symptoms of GERD. Drink a small amount of aloe vera juice (about 1/4 cup) before meals.\nBaking Soda:\n\nBaking soda (sodium bicarbonate) can act as a natural antacid and help neutralize stomach acid. Mix a teaspoon of baking soda in a glass of water and drink it slowly to relieve symptoms.\nChewing Gum:\n\nChewing sugar-free gum after meals can stimulate saliva production, which helps neutralize acid and wash away any remaining food particles in the esophagus.\nStress Reduction:\n\nStress can worsen GERD symptoms, so practicing stress-reduction techniques such as deep breathing, meditation, or yoga may help manage symptoms."], 'Chronic cholestasis': [], 'Drug Reaction': [], 'Peptic ulcer diseae': [], 'AIDS': ["Adherence to Antiretroviral Therapy (ART):\n\nStrict adherence to ART medication regimens is essential for controlling HIV viral load, maintaining immune function, and preventing the progression to AIDS.\nHealthy Diet:\n\nConsuming a balanced diet rich in fruits, vegetables, lean proteins, whole grains, and healthy fats can help support immune function and overall well-being.\nRegular Exercise:\n\nEngaging in regular physical activity can help improve physical fitness, reduce stress, and boost mood. Aim for at least 30 minutes of moderate-intensity exercise most days of the week.\nStress Reduction:\n\nManaging stress through relaxation techniques such as deep breathing, meditation, yoga, or mindfulness can help support emotional well-being.\nAdequate Sleep:\n\nPrioritize getting enough sleep each night to support immune function, energy levels, and overall health. Aim for 7-9 hours of quality sleep per night.\nAvoid Alcohol and Drugs:\n\nAlcohol and recreational drugs can weaken the immune system, interfere with medication adherence, and exacerbate HIV-related complications. Avoid or limit alcohol and drug use.\nSeek Social Support:\n\nBuild a strong support network of friends, family, support groups, or healthcare professionals who understand and can provide emotional support and encouragement.\nPractice Safer Sex:\n\nConsistently use condoms during sexual activity to prevent the transmission of HIV and other sexually transmitted infections (STIs). Discuss pre-exposure prophylaxis (PrEP) and post-exposure prophylaxis (PEP) options with a healthcare provider.\nRegular Medical Monitoring:\n\nAttend regular medical appointments for HIV/AIDS management, monitoring of viral load and CD4 cell count, and screening for opportunistic infections and other complications.\nHygiene Practices:\n\nPractice good hygiene, including regular handwashing, to reduce the risk of infections. Avoid sharing personal items such as toothbrushes, razors, or needles.\nIt's important for individuals with HIV/AIDS to work closely with healthcare providers to develop a comprehensive care plan tailored to their specific needs. This may include medication management, routine monitoring, preventive care, and support services.\n\nDiabetes home remedy\nChatGPT\nWhile there is no cure for diabetes, there are several home remedies and lifestyle changes that may help manage blood sugar levels and improve overall well-being for individuals with diabetes. However, it's essential to consult with a healthcare professional for personalized advice and to ensure these remedies are safe and appropriate for your specific situation. Here are some home remedies and lifestyle changes that may help manage diabetes:\n\nHealthy Diet:\n\nFocus on a balanced diet rich in fruits, vegetables, whole grains, lean proteins, and healthy fats.\nLimit consumption of refined carbohydrates, sugary foods, and beverages that can cause blood sugar spikes.\nMonitor portion sizes and aim for consistent carbohydrate intake throughout the day.\nRegular Exercise:\n\nEngage in regular physical activity to help improve insulin sensitivity and lower blood sugar levels.\nAim for at least 150 minutes of moderate-intensity aerobic exercise per week, such as brisk walking, cycling, or swimming.\nWeight Management:\n\nMaintain a healthy weight through a combination of diet and exercise, as excess body weight can contribute to insulin resistance and elevated blood sugar levels.\nHydration:\n\nDrink plenty of water throughout the day to stay hydrated, as dehydration can affect blood sugar levels and overall health.\nStress Reduction:\n\nPractice stress-reduction techniques such as deep breathing, meditation, yoga, or tai chi to help lower stress hormones and improve blood sugar control.\nAdequate Sleep:\n\nPrioritize getting enough sleep each night, as inadequate sleep can affect insulin sensitivity and blood sugar regulation.\nHerbal Remedies:\n\nSome herbs and supplements may have potential benefits for diabetes management, such as cinnamon, fenugreek, bitter melon, and chromium. However, it's essential to consult with a healthcare professional before using these remedies, as they can interact with medications or have side effects.\nApple Cider Vinegar:\n\nSome studies suggest that apple cider vinegar may help improve insulin sensitivity and lower blood sugar levels. Dilute a tablespoon of apple cider vinegar in a glass of water and drink it before meals, but be cautious as it can cause stomach upset in some individuals.\nBitter Gourd (Bitter Melon):\n\nBitter gourd is a vegetable that may help lower blood sugar levels due to its hypoglycemic properties. Consider adding bitter gourd to your diet, either cooked or juiced, but monitor blood sugar levels closely.\nRegular Monitoring:\n\nMonitor blood sugar levels regularly as directed by your healthcare provider and adjust diet, exercise, and medication accordingly."], 'Diabetes ': [], 'Gastroenteritis': ["Stay Hydrated:\n\nDrink plenty of fluids to prevent dehydration caused by vomiting and diarrhea. Rehydration solutions like oral rehydration salts (ORS) or electrolyte solutions (e.g., Pedialyte) can help replace lost fluids and electrolytes.\nBRAT Diet:\n\nFollow a bland diet consisting of easily digestible foods such as bananas, rice, applesauce, and toast. These foods can help settle the stomach and provide essential nutrients.\nGinger:\n\nGinger has anti-nausea properties and may help alleviate symptoms of nausea and vomiting. Try ginger tea, ginger ale (flat), or ginger supplements to help settle the stomach.\nMint:\n\nPeppermint tea or sucking on peppermint candies may help alleviate symptoms of nausea and soothe the digestive tract.\nProbiotics:\n\nProbiotics, found in foods like yogurt or in supplement form, may help restore the balance of beneficial gut bacteria and promote recovery from gastroenteritis.\nAvoid Irritating Foods:\n\nAvoid foods and beverages that can irritate the stomach and exacerbate symptoms, such as spicy, greasy, or acidic foods, caffeine, and alcohol.\nStay Rested:\n\nGet plenty of rest to allow your body to recover and conserve energy.\nBRATY Diet:\n\nIn addition to the BRAT diet, you can add yogurt to your diet. Yogurt contains probiotics that can help restore the balance of gut bacteria and promote digestive health.\nRice Water:\n\nConsuming rice water (the water drained from boiled rice) may help soothe the digestive tract and provide hydration.\nChamomile Tea:\n\nChamomile tea has anti-inflammatory and calming properties that may help alleviate symptoms of gastroenteritis, including abdominal cramps and discomfort.\nRemember to listen to your body and avoid overeating or consuming foods that worsen symptoms. If symptoms persist or worsen, or if you experience signs of dehydration such as dry mouth, excessive thirst, decreased urine output, dizziness, or weakness, seek medical attention promptly. Additionally, seek medical attention if you experience severe abdominal pain, high fever, bloody stools, or signs of dehydration in children or older adults.\n\n\n      Bronchial Asthma home remedy\nChatGPT\nBronchial asthma is a chronic respiratory condition characterized by inflammation and narrowing of the airways, leading to symptoms such as wheezing, shortness of breath, coughing, and chest tightness. While there is no cure for asthma, there are several home remedies and lifestyle modifications that can help manage symptoms and improve overall lung function. However, it's essential to work closely with a healthcare professional to develop a comprehensive asthma management plan tailored to your individual needs. Here are some home remedies and lifestyle changes that may help manage bronchial asthma:\n\nIdentify and Avoid Triggers:\n\nIdentify and avoid asthma triggers such as allergens (e.g., pollen, dust mites, pet dander), air pollution, smoke, strong odors, and respiratory infections.\nStay Hydrated:\n\nDrink plenty of fluids to help keep airway secretions thin and promote easier breathing.\nMaintain a Healthy Diet:\n\nConsume a balanced diet rich in fruits, vegetables, whole grains, lean proteins, and healthy fats to support overall health and lung function.\nOmega-3 Fatty Acids:\n\nFoods rich in omega-3 fatty acids, such as fatty fish (salmon, mackerel, sardines), flaxseeds, chia seeds, and walnuts, may help reduce inflammation and improve lung function.\nVitamin D:\n\nEnsure adequate vitamin D intake through sunlight exposure or dietary sources (e.g., fortified foods, fatty fish, egg yolks) to support immune function and reduce asthma exacerbations.\nBreathing Exercises:\n\nPractice breathing exercises such as diaphragmatic breathing, pursed-lip breathing, and yoga to improve lung function, reduce stress, and manage asthma symptoms.\nSteam Inhalation:\n\nInhaling steam from a bowl of hot water or taking a warm shower can help open up the airways and provide relief from asthma symptoms.\nHoney:\n\nConsuming honey may help soothe the throat and reduce coughing associated with asthma. Mix a teaspoon of honey in warm water or herbal tea and drink it slowly.\nEssential Oils:\n\nSome essential oils, such as eucalyptus, peppermint, and lavender, may help relieve asthma symptoms when used in a diffuser or diluted and applied topically. Be cautious if using essential oils, as they can trigger asthma symptoms in some individuals.\nMaintain a Clean Environment:\n\nKeep your home clean and free of dust, pet dander, mold, and other allergens that can trigger asthma symptoms. Use allergen-proof covers on pillows and mattresses, vacuum regularly, and use air purifiers with HEPA filters."], 'Bronchial Asthma': [], 'Hypertension ': [], 'Migraine': [], 'Cervical spondylosis': [], 'Paralysis (brain hemorrhage)': [], 'Jaundice': ['Stay Hydrated:\n\nDrink plenty of water throughout the day to help flush toxins from the body and prevent dehydration.\nHealthy Diet:\n\nFollow a well-balanced diet rich in fruits, vegetables, whole grains, lean proteins, and healthy fats. Avoid fatty, processed, and spicy foods.\nIncorporate foods that support liver health, such as leafy greens, cruciferous vegetables (e.g., broccoli, Brussels sprouts), garlic, turmeric, and fruits high in antioxidants.\nLimit consumption of alcohol, as it can exacerbate liver damage and worsen jaundice.\nHerbal Remedies:\n\nMilk thistle is an herb that may help support liver function and protect against liver damage. Consider taking milk thistle supplements under the guidance of a healthcare professional.\nAvoid Hepatotoxic Substances:\n\nAvoid exposure to hepatotoxic substances, such as certain medications, chemicals, and environmental toxins, which can further damage the liver and worsen jaundice.\nRest and Relaxation:\n\nGet plenty of rest and avoid strenuous physical activity to allow the body to heal and recover.\nAvoid Raw Seafood:\n\nAvoid consuming raw or undercooked seafood, as it may harbor harmful bacteria and parasites that can worsen liver function.\nLemon Water:\n\nDrinking lemon water may help stimulate bile production and promote liver detoxification. Squeeze fresh lemon juice into a glass of warm water and drink it first thing in the morning on an empty stomach.\nCarrot Juice:\n\nCarrot juice is rich in antioxidants and vitamin A, which may help support liver health and improve jaundice symptoms. Drink freshly prepared carrot juice daily.\nBarley Water:\n\nBarley water may help flush toxins from the body and support liver function. Boil barley in water, strain the liquid, and drink it warm or cold.\nMonitor Symptoms:\n\nKeep track of jaundice symptoms and seek medical attention if they worsen or if you experience additional symptoms such as abdominal pain, fever, nausea, vomiting, or changes in mental status.'], 'Malaria': [], 'Chicken pox': [], 'Dengue': ['Stay Hydrated:\n\nDrink plenty of fluids, such as water, electrolyte solutions, coconut water, and clear soups, to prevent dehydration and replace lost fluids due to fever, sweating, and vomiting.\nRest:\n\nGet plenty of rest and avoid strenuous activities to allow the body to recover from the illness. Lie down and elevate your legs to help reduce swelling and promote circulation.\nPain Relief:\n\nTake over-the-counter pain relievers such as acetaminophen (paracetamol) to reduce fever and alleviate headache, muscle, and joint pain. Avoid aspirin and nonsteroidal anti-inflammatory drugs (NSAIDs) such as ibuprofen and naproxen, as they can increase the risk of bleeding.\nCool Compresses:\n\nApply cool, damp compresses or ice packs wrapped in a cloth to the forehead, neck, and body to help reduce fever and relieve discomfort.\nDiet:\n\nEat a well-balanced diet consisting of easily digestible foods such as fruits, vegetables, lean proteins, and whole grains to support immune function and promote recovery. Avoid fatty, spicy, and heavy foods that may exacerbate nausea and vomiting.\nPapaya Leaf Extract:\n\nSome studies suggest that papaya leaf extract may help increase platelet count in individuals with dengue fever. However, more research is needed to confirm its effectiveness. Consult with a healthcare professional before using papaya leaf extract.\nTulsi (Holy Basil):\n\nTulsi leaves have antiviral and immune-boosting properties and may help alleviate symptoms of dengue fever. Drink tulsi tea or chew fresh tulsi leaves to support immune function.\nNeem Leaves:\n\nNeem leaves have antiviral properties and may help boost immunity. Drink neem leaf extract or chew fresh neem leaves to support immune function during dengue fever.\nMosquito Protection:\n\nProtect yourself from mosquito bites by wearing long-sleeved clothing, using mosquito repellents containing DEET or picaridin, and sleeping under mosquito nets, especially during the daytime when Aedes mosquitoes are most active.\nSeek Medical Attention:\n\nSeek medical attention promptly if you suspect dengue fever or experience severe symptoms such as persistent vomiting, severe abdominal pain, difficulty breathing, bleeding gums, or signs of shock'], 'Typhoid': ['Hydration:\n\nDrink plenty of fluids, such as water, electrolyte solutions, clear soups, coconut water, and herbal teas, to prevent dehydration and replace lost fluids due to fever, sweating, vomiting, and diarrhea.\nRest:\n\nGet plenty of rest and avoid strenuous activities to allow the body to recover from the illness. Lie down and elevate your legs to help reduce fever and promote relaxation.\nNutrition:\n\nEat a well-balanced diet consisting of easily digestible foods such as fruits, vegetables, lean proteins, and whole grains to support immune function and promote recovery. Avoid fatty, spicy, and heavy foods that may exacerbate gastrointestinal symptoms.\nProbiotics:\n\nProbiotic-rich foods such as yogurt, kefir, and fermented vegetables may help restore the balance of beneficial gut bacteria and improve gastrointestinal symptoms associated with typhoid fever.\nOral Rehydration Therapy (ORT):\n\nPrepare oral rehydration solutions (ORS) at home using a mixture of clean water, salt, and sugar to help replace lost fluids, electrolytes, and glucose. Commercial ORS packets are also available and can be purchased at pharmacies.\nGinger:\n\nGinger has anti-inflammatory and antimicrobial properties and may help alleviate symptoms such as nausea, vomiting, and abdominal pain associated with typhoid fever. Drink ginger tea or chew on fresh ginger slices.\nTurmeric:\n\nTurmeric contains curcumin, which has anti-inflammatory and antimicrobial properties. Add turmeric powder to soups, stews, or warm milk to help boost immune function and reduce inflammation.\nBasil (Tulsi):\n\nBasil leaves have antibacterial properties and may help reduce fever and alleviate symptoms of typhoid fever. Drink tulsi tea or chew fresh basil leaves.\nGarlic:\n\nGarlic has antimicrobial properties and may help fight bacterial infections. Consume raw garlic cloves or add crushed garlic to soups, salads, or cooked dishes.\nMaintain Hygiene:\n\nPractice good hygiene by washing hands frequently with soap and water, especially before eating, after using the toilet, and after handling food. Use clean utensils and cook food thoroughly to prevent contamination.'], 'Tuberculosis': [], 'Common Cold': [], 'Dimorphic hemmorhoids(piles)': ['High-Fiber Diet:\n\nEat a diet rich in high-fiber foods such as fruits, vegetables, whole grains, legumes, and nuts. Fiber helps soften stools and promote regular bowel movements, reducing strain during bowel movements.\nHydration:\n\nDrink plenty of fluids, especially water, to stay hydrated and help prevent constipation. Aim for at least 8 glasses of water per day.\nSitz Baths:\n\nTake warm sitz baths for 10 to 15 minutes several times a day to help soothe anal discomfort, reduce inflammation, and promote healing. You can add Epsom salts or witch hazel to the bathwater for added relief.\nTopical Treatments:\n\nApply over-the-counter hemorrhoid creams, ointments, or suppositories containing ingredients such as hydrocortisone, witch hazel, or lidocaine to help relieve pain, itching, and inflammation.\nCold Compresses:\n\nApply cold compresses or ice packs wrapped in a cloth to the affected area for 10 to 15 minutes at a time to help reduce swelling and numb pain.\nKeep the Anal Area Clean:\n\nGently clean the anal area with warm water and mild soap after bowel movements to prevent irritation and infection. Avoid using harsh or scented toiletries that may aggravate hemorrhoids.\nAvoid Straining:\n\nAvoid straining during bowel movements by not delaying the urge to have a bowel movement and not sitting on the toilet for extended periods. Use a stool softener if necessary to ease bowel movements.\nUse Soft, Moist Wipes:\n\nUse soft, moist wipes or unscented, alcohol-free baby wipes instead of dry toilet paper to clean the anal area after bowel movements.\nElevate the Feet:\n\nPlace your feet on a small stool or footrest while sitting on the toilet to raise your knees above your hips, which can help facilitate bowel movements and reduce strain.\nMaintain a Healthy Weight and Exercise Regularly:\n\nMaintain a healthy weight and engage in regular physical activity to improve bowel function, reduce pressure on the rectum and anus, and prevent constipation.'], 'Hypothyroidism': [], 'Hyperthyroidism': ["Healthy Diet:\n\nEat a balanced diet rich in fruits, vegetables, whole grains, and lean proteins. Avoid excessive iodine intake, as it can exacerbate thyroid hormone production. Limit iodine-rich foods such as seaweed, seafood, iodized salt, and dairy products.\nStress Management:\n\nPractice stress-reduction techniques such as deep breathing, meditation, yoga, tai chi, or progressive muscle relaxation to help reduce stress levels, which can impact thyroid function.\nRegular Exercise:\n\nEngage in regular physical activity, such as walking, cycling, swimming, or yoga, to help manage stress, improve energy levels, and support overall health. Aim for at least 30 minutes of moderate-intensity exercise most days of the week.\nLimit Stimulants:\n\nReduce consumption of stimulants such as caffeine and nicotine, as they can exacerbate symptoms of hyperthyroidism such as palpitations, nervousness, and insomnia.\nLemon Balm:\n\nLemon balm, also known as Melissa officinalis, has calming properties and may help reduce anxiety and promote relaxation. Drink lemon balm tea or take lemon balm supplements after consulting with a healthcare professional.\nAvoid Goitrogenic Foods:\n\nSome foods contain compounds known as goitrogens, which can interfere with thyroid hormone production. Limit intake of goitrogenic foods such as cruciferous vegetables (e.g., cabbage, broccoli, Brussels sprouts), soy products, and millet.\nAdequate Sleep:\n\nPrioritize getting enough restful sleep each night to support overall health and well-being. Aim for 7-9 hours of quality sleep per night.\nHerbal Supplements:\n\nSome herbs such as bugleweed (Lycopus europaeus) and motherwort (Leonurus cardiaca) may help reduce thyroid hormone levels and alleviate symptoms of hyperthyroidism. However, it's essential to consult with a healthcare professional before using herbal supplements, as they can interact with medications and may not be suitable for everyone.\nRegular Thyroid Function Monitoring:\n\nSchedule regular follow-up appointments with your healthcare provider to monitor thyroid function through blood tests and adjust treatment as necessary.\nAvoid Excessive Iodine:\n\nExcessive iodine intake can worsen hyperthyroidism. Avoid supplements containing iodine, as well as foods high in iodine such as seaweed and iodized salt."], 'Hypoglycemia': ["Fast-Acting Carbohydrates:\n\nConsume fast-acting carbohydrates to quickly raise blood sugar levels. Examples include:\nGlucose tablets or gel\nFruit juice\nRegular soda (not diet)\nHoney or maple syrup\nHard candies, such as glucose tablets or jellybeans\nComplex Carbohydrates:\n\nAfter consuming fast-acting carbohydrates to raise blood sugar levels, follow up with complex carbohydrates to sustain blood sugar levels over time. Examples include whole grains, legumes, fruits, and vegetables.\nProtein and Healthy Fats:\n\nInclude protein and healthy fats in your meals and snacks to help stabilize blood sugar levels and prevent rapid spikes and drops. Examples include lean proteins (e.g., poultry, fish, tofu), nuts, seeds, avocados, and olive oil.\nFrequent Meals and Snacks:\n\nEat small, frequent meals and snacks throughout the day to help maintain stable blood sugar levels. Avoid long periods of fasting or skipping meals, as this can increase the risk of hypoglycemia.\nRegular Monitoring:\n\nMonitor blood sugar levels regularly, especially if you have diabetes or are at risk of hypoglycemia. Keep a log of your blood sugar readings and track any symptoms of hypoglycemia.\nCarry Emergency Snacks:\n\nCarry emergency snacks with you, such as glucose tablets, crackers, nuts, or dried fruit, to quickly raise blood sugar levels in case of hypoglycemia.\nAvoid Excessive Alcohol:\n\nLimit alcohol consumption, as it can lower blood sugar levels and increase the risk of hypoglycemia, especially if you're taking diabetes medications.\nRegular Exercise:\n\nEngage in regular physical activity, as exercise can help improve insulin sensitivity and regulate blood sugar levels. However, be mindful of the timing and intensity of exercise to prevent hypoglycemia during or after physical activity.\nStay Hydrated:\n\nDrink plenty of water throughout the day to stay hydrated, as dehydration can exacerbate symptoms of hypoglycemia.\nConsult with a Healthcare Professional:\n\nIf you experience frequent episodes of hypoglycemia or have concerns about managing your blood sugar levels, consult with a healthcare professional for personalized guidance and recommendations."], 'Osteoarthristis': ['Maintain a Healthy Weight:\n\nExcess weight can put additional stress on weight-bearing joints such as the knees, hips, and spine, worsening symptoms of osteoarthritis. Maintain a healthy weight through a balanced diet and regular exercise to reduce joint strain and improve mobility.\nExercise Regularly:\n\nEngage in low-impact exercises such as walking, swimming, cycling, or tai chi to strengthen muscles, improve joint flexibility, and reduce pain associated with osteoarthritis. Aim for at least 30 minutes of moderate-intensity exercise most days of the week.\nHot and Cold Therapy:\n\nApply heat packs or warm towels to affected joints to help reduce stiffness and promote relaxation of muscles and tissues. Alternatively, use cold packs or ice packs to reduce inflammation and numb pain. Alternate between heat and cold therapy as needed.\nMaintain Joint Mobility:\n\nPerform gentle stretching exercises and range-of-motion exercises to improve joint flexibility and prevent stiffness. Consult with a physical therapist for guidance on appropriate exercises for your condition.\nUse Assistive Devices:\n\nUse assistive devices such as canes, walkers, or braces to support and stabilize joints, reduce pain, and improve mobility, especially during activities that aggravate symptoms.\nAcupuncture:\n\nSome people find relief from osteoarthritis symptoms through acupuncture, a traditional Chinese therapy that involves inserting thin needles into specific points on the body to promote pain relief and improve joint function. Consult with a qualified acupuncturist for treatment.\nTopical Treatments:\n\nApply topical treatments such as over-the-counter creams, gels, or patches containing ingredients like capsaicin, menthol, or salicylates to the affected joints to help reduce pain and inflammation.\nDietary Supplements:\n\nConsider taking dietary supplements such as glucosamine, chondroitin sulfate, or turmeric/curcumin, which may help support joint health and reduce symptoms of osteoarthritis. Consult with a healthcare professional before starting any new supplements, especially if you have underlying health conditions or are taking medications.\nHealthy Diet:\n\nFollow a balanced diet rich in fruits, vegetables, whole grains, lean proteins, and healthy fats to support overall health and well-being. Include foods rich in omega-3 fatty acids (e.g., fatty fish, flaxseeds, chia seeds) and antioxidants (e.g., berries, leafy greens) to help reduce inflammation.\nManage Stress:\n\nPractice stress-reduction techniques such as deep breathing, meditation, yoga, or mindfulness to help manage stress levels, as stress can exacerbate symptoms of osteoarthritis.'], '(vertigo) Paroymsal  Positional Vertigo': []}

def get_db_connection():
    conn = sqlite3.connect('solution.db')
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

# Route for handling login requests
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Get a database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query the database for the user's credentials
        cursor.execute('SELECT * FROM solution WHERE username = ? AND password = ?', (username, password))
        user_data = cursor.fetchone()  # Fetch one row

        # Close the cursor and database connection
        cursor.close()
        conn.close()

        # Check if the user exists
        if user_data:
            # Redirect to the index page after successful login
            return redirect(url_for('index'))
        else:
            error = 'Invalid credentials. Please try again.'
            return render_template('login.html', error=error)
    
    # Render the login page for GET requests
    return render_template('login.html')

conn = sqlite3.connect('solution.db')
cursor = conn.cursor()
conn.commit()
conn.close()

@app.route('/signup', methods=['GET', 'POST'])
def signup_page():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')

        # Check if passwords match
        if password != confirm_password:
            return render_template('signup.html', error='Passwords do not match.')

        # Connect to the database and insert user data
        conn = sqlite3.connect('solution.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO solution (username, email, password) VALUES (?, ?, ?)', (username, email, password))
        conn.commit()
        conn.close()

        # Redirect to signup success page
        return redirect(url_for('signup_success'))

    # Render the signup form
    return render_template('signup.html')

@app.route('/signup_success')
def signup_success():
    return render_template('signup_success.html')


# Route to serve the index.html file
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/process_form', methods=['POST'])
def process_form():
    # Get the selected symptoms from the form
    symptoms = request.json.get('symptoms')

    # Create an array to store the symptoms data
    symptoms_array = np.array([[1 if sym in symptoms else 0 for sym in all_symptoms]])

    # Make predictions using the ensemble classifier (not defined in your code snippet)
    predicted_label = ensemble_classifier.predict(symptoms_array)
    predicted_disease = le.inverse_transform(predicted_label)

    remedy_info = home_remedies.get(predicted_disease[0], [])

    # Return the predicted disease and home remedy as JSON response
    return jsonify({'predicted_disease': predicted_disease[0], 'remedy_info': remedy_info})


def send_notification(title, message, description):
    notification.notify(
        title=title,
        message=f"{message}\n\nDescription: {description}",
        timeout=1  # Notification timeout in seconds
    )
    print(f"Notification sent - Title: {title}, Message: {message}, Description: {description}")

def schedule_notification(title, message, description, scheduled_time):
    current_time = datetime.now().strftime("%H:%M")
    if current_time == scheduled_time:
        send_notification(title, message, description)
    else:
        delay = (datetime.strptime(scheduled_time, "%H:%M") - datetime.strptime(current_time, "%H:%M")).total_seconds()
        if delay > 0:
            # Schedule the notification in a separate thread
            def send_after_delay():
                time.sleep(delay)
                send_notification(title, message, description)
            
            thread = Thread(target=send_after_delay)
            thread.start()

@app.route('/notification.html', methods=['GET', 'POST'])
def show_notification():
    if request.method == 'POST':
        user_time = request.form.get('notification-time')
        description = request.form.get('notification-description')
        if user_time:
            notification_title = "Health care monitor"
            notification_message ="!"
            schedule_notification(notification_title, notification_message, description, user_time)
            return render_template('notification.html', user_time=user_time, description=description)
        else:
            return render_template('notification.html', error="Please enter a valid notification time.")
    return render_template('notification.html')

if __name__ == '__main__':
    app.run(debug=True)