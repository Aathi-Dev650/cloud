"""Seed reviewed editorial disease guidance documents into Firestore."""
from django.core.management.base import BaseCommand, CommandError
from firebase.firestore import client as firestore_db


GUIDANCE = [
    {
        'model_label': 'Tomato___Early_blight',
        'crop': 'tomato', 'disease': 'early blight',
        'symptoms': ['Brown circular spots with concentric rings', 'Yellowing around older leaf lesions'],
        'solution': ['Remove badly affected leaves using clean tools', 'Seek locally approved crop-protection advice before treatment'],
        'prevention': ['Avoid prolonged leaf wetness', 'Remove infected plant debris after harvest'],
    },
    {
        'model_label': 'Tomato___Late_blight',
        'crop': 'tomato', 'disease': 'late blight',
        'symptoms': ['Dark water-soaked leaf patches', 'Pale fungal growth may appear in humid conditions'],
        'solution': ['Isolate affected plants and seek local extension advice promptly', 'Remove severely infected plant material safely'],
        'prevention': ['Improve airflow between plants', 'Avoid overhead irrigation late in the day'],
    },
    {
        'model_label': 'Tomato___healthy',
        'crop': 'tomato', 'disease': 'healthy',
        'symptoms': ['No disease symptoms detected by the model'],
        'solution': ['Continue regular field inspection and normal crop care'],
        'prevention': ['Use clean tools and healthy planting material', 'Monitor leaves after wet weather'],
    },
    {
        'model_label': 'Potato___Early_blight',
        'crop': 'potato', 'disease': 'early blight',
        'symptoms': ['Brown target-like spots on older leaves', 'Yellowing leaf tissue around lesions'],
        'solution': ['Remove severely affected foliage', 'Consult local crop-protection guidance before treatment'],
        'prevention': ['Rotate crops where practical', 'Keep plant debris out of the field'],
    },
    {
        'model_label': 'Potato___Late_blight',
        'crop': 'potato', 'disease': 'late blight',
        'symptoms': ['Irregular dark leaf lesions', 'White growth can appear under leaves during humid weather'],
        'solution': ['Seek local agricultural advice immediately', 'Remove heavily infected material carefully'],
        'prevention': ['Inspect frequently in cool, wet periods', 'Improve field drainage and airflow'],
    },
    {
        'model_label': 'Potato___healthy',
        'crop': 'potato', 'disease': 'healthy',
        'symptoms': ['No disease symptoms detected by the model'],
        'solution': ['Continue regular crop care and observation'],
        'prevention': ['Use disease-free seed potatoes', 'Maintain field sanitation'],
    },
]


NOTICE = 'Use only a product registered for this crop/use in India; follow its current label and local extension advice.'


def entry(label, crop, disease, symptoms, solution, prevention):
    return {'model_label': label, 'crop': crop, 'disease': disease, 'symptoms': symptoms, 'solution': solution, 'prevention': prevention}


# Tamil Nadu-oriented entries matching the labels in ml/artifacts/class_names.json.
GUIDANCE.extend([
    entry('Pepper__bell___Bacterial_spot', 'pepper bell', 'Bacterial spot', ['Small dark water-soaked spots', 'Yellow halos and leaf drop can occur'], ['Remove badly affected leaves; avoid handling wet plants', f'Ask the local horticulture officer about a copper-based bactericide. {NOTICE}'], ['Use healthy seed/transplants, sanitize tools, and avoid overhead irrigation']),
    entry('Pepper__bell___healthy', 'pepper bell', 'healthy', ['No disease symptoms detected by the model'], ['No medicine is indicated; continue regular scouting'], ['Use healthy planting material and keep foliage dry where practical']),
    entry('Potato___Early_blight', 'potato', 'Early blight', ['Brown target-like spots on older leaves', 'Yellowing around lesions'], ['Remove severely affected foliage', f'A locally registered mancozeb-based fungicide may be considered with Tamil Nadu extension advice. {NOTICE}'], ['Rotate crops and remove potato/tomato debris']),
    entry('Potato___Late_blight', 'potato', 'Late blight', ['Water-soaked patches that turn brown or black', 'White growth may occur beneath leaves'], ['Act promptly and seek local extension advice', f'TNAU lists protective mancozeb or zineb products. {NOTICE}'], ['Use healthy seed tubers and do not store visibly infected tubers']),
    entry('Potato___healthy', 'potato', 'healthy', ['No disease symptoms detected by the model'], ['No medicine is indicated; continue regular crop care'], ['Use disease-free seed potatoes and maintain field sanitation']),
    entry('Tomato_Bacterial_spot', 'tomato', 'Bacterial spot', ['Small dark water-soaked spots', 'Yellow halo or spotting on leaves and fruit'], ['Remove affected leaves and avoid handling wet plants', f'Ask the local horticulture officer about a copper-based bactericide. {NOTICE}'], ['Use clean seed/transplants, sanitize tools, and reduce splash irrigation']),
    entry('Tomato_Early_blight', 'tomato', 'Early blight', ['Brown concentric-ring spots with yellow margins', 'Older leaves are often affected first'], ['Remove heavily affected foliage', f'TNAU advises mancozeb for tomato early blight. {NOTICE}'], ['Remove crop debris, rotate crops, and avoid prolonged leaf wetness']),
    entry('Tomato_Late_blight', 'tomato', 'Late blight', ['Irregular water-soaked green-brown to black patches', 'Rapid blighting in cool, humid weather'], ['Isolate affected plants and contact local extension support promptly', f'Use a locally registered late-blight fungicide selected with extension advice. {NOTICE}'], ['Improve airflow and remove infected crop residues']),
    entry('Tomato_Leaf_Mold', 'tomato', 'Leaf mold', ['Yellow upper-leaf patches', 'Olive-green to brown mold may appear beneath leaves'], ['Improve ventilation and remove badly affected leaves', f'Ask local extension staff for a registered fungicide if it is spreading. {NOTICE}'], ['Lower humidity, increase spacing, and avoid overhead irrigation']),
    entry('Tomato_Septoria_leaf_spot', 'tomato', 'Septoria leaf spot', ['Small spots with grey centres and dark margins', 'Lower leaves yellow and may drop'], ['Remove affected foliage and crop debris', f'TNAU lists fluxapyroxad plus pyraclostrobin for this disease. {NOTICE}'], ['Mulch to reduce soil splash and avoid wet foliage']),
    entry('Tomato_Spider_mites_Two_spotted_spider_mite', 'tomato', 'Two-spotted spider mite', ['Fine pale stippling or bronzing', 'Fine webbing may occur in severe infestations'], ['Check leaf undersides and reduce dust/water stress', f'TNAU guidance lists wettable sulphur for mite management. {NOTICE}'], ['Conserve beneficial insects and inspect regularly in hot, dry weather']),
    entry('Tomato__Target_Spot', 'tomato', 'Target spot', ['Brown circular lesions, sometimes with concentric rings', 'Leaf yellowing and drop may follow'], ['Remove severely affected foliage and seek local extension advice', f'Use a locally registered fungicide recommended for the confirmed diagnosis. {NOTICE}'], ['Improve airflow, avoid splash irrigation, and remove crop debris']),
    entry('Tomato__Tomato_YellowLeaf__Curl_Virus', 'tomato', 'Tomato yellow leaf curl virus', ['Leaf curl, yellowing, and stunting', 'Bushy growth with shortened internodes'], ['There is no curative medicine; remove infected plants early', f'TNAU recommends whitefly traps and locally registered vector-control products. {NOTICE}'], ['Use healthy seedlings, yellow sticky traps, barrier crops, and remove weed hosts']),
    entry('Tomato__Tomato_mosaic_virus', 'tomato', 'Tomato mosaic virus', ['Light and dark green mosaic pattern', 'Leaf distortion and stunted growth'], ['There is no curative medicine; remove infected plants and disinfect hands/tools', 'Do not use tobacco-contaminated hands or tools around plants'], ['Use certified seed and avoid mechanical spread']),
    entry('Tomato_healthy', 'tomato', 'healthy', ['No disease symptoms detected by the model'], ['No medicine is indicated; continue routine scouting'], ['Maintain sanitation, balanced irrigation, and monitoring']),
])


class Command(BaseCommand):
    help = 'Upsert reviewed disease guidance documents into Firestore.'

    def handle(self, *args, **options):
        try:
            collection = firestore_db().collection('diseases')
            for item in GUIDANCE:
                collection.document(item['model_label']).set(item, merge=True)
        except Exception as exc:
            raise CommandError(f'Could not seed disease guidance: {exc}') from exc
        self.stdout.write(self.style.SUCCESS(f'Seeded {len(GUIDANCE)} disease guidance records.'))
