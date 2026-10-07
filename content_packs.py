"""Curated, reviewable content rules for Storyworld v23.

Everything here is plain data that a parent, teacher or reviewer can read.
The model receives these rules as constraints; it never extends the facts,
the sacred references or the support guidance on its own.
"""

from __future__ import annotations

# --------------------------------------------------------------------------
# Languages (16). `locale` is the narration locale requested from /tts/book.
# --------------------------------------------------------------------------
LANGUAGES = {
    "English": {"locale": "en-US", "native": "English", "rtl": False},
    "Spanish": {"locale": "es-ES", "native": "Español", "rtl": False},
    "Russian": {"locale": "ru-RU", "native": "Русский", "rtl": False},
    "Ukrainian": {"locale": "uk-UA", "native": "Українська", "rtl": False},
    "German": {"locale": "de-DE", "native": "Deutsch", "rtl": False},
    "French": {"locale": "fr-FR", "native": "Français", "rtl": False},
    "Italian": {"locale": "it-IT", "native": "Italiano", "rtl": False},
    "Portuguese": {"locale": "pt-BR", "native": "Português", "rtl": False},
    "Polish": {"locale": "pl-PL", "native": "Polski", "rtl": False},
    "Turkish": {"locale": "tr-TR", "native": "Türkçe", "rtl": False},
    "Arabic": {"locale": "ar-JO", "native": "العربية", "rtl": True},
    "Hebrew": {"locale": "he-IL", "native": "עברית", "rtl": True},
    "Hindi": {"locale": "hi-IN", "native": "हिन्दी", "rtl": False},
    "Chinese": {"locale": "zh-CN", "native": "中文", "rtl": False},
    "Japanese": {"locale": "ja-JP", "native": "日本語", "rtl": False},
    "Korean": {"locale": "ko-KR", "native": "한국어", "rtl": False},
}

REFLECTIONS = {
    "English": "What did you notice in this part of the story?",
    "Spanish": "¿Qué recuerdas de esta parte de la historia?",
    "Russian": "Что тебе запомнилось в этой части истории?",
    "Ukrainian": "Що тобі запам’яталося в цій частині історії?",
    "German": "Woran erinnerst du dich aus diesem Teil der Geschichte?",
    "French": "De quoi te souviens-tu dans cette partie de l’histoire ?",
    "Italian": "Che cosa ricordi di questa parte della storia?",
    "Portuguese": "O que você lembra desta parte da história?",
    "Polish": "Co zapamiętałeś z tej części opowieści?",
    "Turkish": "Hikâyenin bu bölümünden aklında ne kaldı?",
    "Arabic": "ماذا تتذكر من هذا الجزء من القصة؟",
    "Hebrew": "מה זכרת מהחלק הזה בסיפור?",
    "Hindi": "कहानी के इस हिस्से में तुम्हें क्या याद रहा?",
    "Chinese": "故事的这一部分，你记住了什么？",
    "Japanese": "この場面で心に残ったことは何ですか？",
    "Korean": "이 장면에서 무엇이 기억에 남았나요?",
}

# --------------------------------------------------------------------------
# Reading stages: independent from chronological age.
# --------------------------------------------------------------------------
READING_STAGES = {
    1: {"name": "Listener", "words": (55, 75),
        "rule": "Read-aloud text for a child who does not read yet. Very short sentences of 5 to 8 words, strong rhythm, gentle repetition of one key phrase."},
    2: {"name": "Sound explorer", "words": (60, 80),
        "rule": "Short sentences of 5 to 8 words with everyday words. Repeat important words so they can be recognised by sight."},
    3: {"name": "First words", "words": (70, 90),
        "rule": "Sentences of 6 to 9 words. Common concrete words. Repeat each new word at least twice on the page."},
    4: {"name": "Beginning reader", "words": (80, 100),
        "rule": "Short sentences with familiar words. Introduce at most one new word and make its meaning clear from the action."},
    5: {"name": "Growing reader", "words": (95, 115),
        "rule": "Sentences of 8 to 12 words. Introduce two new words and explain each through context, never with a dictionary definition."},
    6: {"name": "Confident reader", "words": (110, 125),
        "rule": "Richer vocabulary and some compound sentences. New words always appear with enough context to be understood."},
    7: {"name": "Independent reader", "words": (120, 140),
        "rule": "Varied sentence length, precise verbs, a little figurative language, and subject words explained inside the story."},
    8: {"name": "Advanced reader", "words": (130, 150),
        "rule": "Layered plot, precise domain vocabulary, sentences up to 16 words, and a moment that invites the reader to infer something."},
}
LEGACY_READING_LEVELS = {"Read together": 2, "Beginning reader": 4, "Independent reader": 6}

# --------------------------------------------------------------------------
# Recurring companions. Fixed visual descriptors keep illustrations stable.
# --------------------------------------------------------------------------
COMPANIONS = [
    {"key": "fox", "name": "Pip", "role": "a curious fox mapmaker",
     "visual": "a small orange fox with a white-tipped tail, wearing a green satchel full of rolled maps"},
    {"key": "owl", "name": "Luma", "role": "a shy young owl who loves questions",
     "visual": "a small round grey owl with large amber eyes and a tiny blue scarf"},
    {"key": "ranger", "name": "Rowan", "role": "a cheerful park ranger",
     "visual": "a friendly adult park ranger with a wide-brimmed tan hat, olive jacket and a brass whistle"},
    {"key": "cloud", "name": "Nimbo", "role": "a small cloud that collects sounds",
     "visual": "a small soft white cloud character with rosy cheeks, carrying a tiny glass jar"},
    {"key": "gardener", "name": "Mira", "role": "a patient gardener",
     "visual": "a kind adult gardener with a straw hat, yellow gloves and a blue watering can"},
    {"key": "biologist", "name": "Sol", "role": "a junior marine biologist",
     "visual": "a young adult scientist in a teal wetsuit with a waterproof notebook and round goggles on the forehead"},
    {"key": "seal", "name": "Bubble", "role": "a playful seal who lives by the lighthouse",
     "visual": "a small spotted grey seal with long whiskers and a red ball"},
    {"key": "inventor", "name": "Tavi", "role": "a young inventor with a paper kite",
     "visual": "a teenager with a tool belt, rolled-up sleeves and a bright red paper kite"},
    {"key": "musician", "name": "Lio", "role": "a traveling musician",
     "visual": "a gentle adult musician with a patched purple coat and a small wooden ukulele"},
    {"key": "bee", "name": "Zuzu", "role": "a careful bee observer",
     "visual": "a round fuzzy honey bee with small glasses and a striped yellow scarf"},
]

# --------------------------------------------------------------------------
# Science & Nature. Facts are conservative, school-level statements.
# --------------------------------------------------------------------------
SCIENCE_FACTS = {
    "Stars and planets": [
        "Earth travels around the Sun in about 365 days.",
        "Earth rotates once in about 24 hours.",
        "The Moon travels around Earth.",
        "The Sun is a star.",
    ],
    "Our Earth": [
        "Oceans cover most of Earth's surface.",
        "Water can evaporate, condense into clouds, and fall as precipitation.",
        "Earth's rotation gives us day and night.",
    ],
    "Plants and animals": [
        "Plants use light, water, and carbon dioxide to make food.",
        "Many flowering plants rely on pollinators.",
        "A habitat provides living things with food, water, shelter, and space.",
    ],
    "Oceans": [
        "Sea water is salty.",
        "Whales are mammals and breathe air.",
        "Coral reefs are built by tiny animals called coral polyps.",
        "Tides are caused mainly by the Moon's gravity.",
    ],
    "Dinosaurs": [
        "Dinosaurs lived millions of years ago, long before people.",
        "Scientists learn about dinosaurs from fossils.",
        "Some dinosaurs ate plants and some ate meat.",
        "Birds are living relatives of dinosaurs.",
    ],
    "Weather": [
        "Wind is moving air.",
        "Clouds are made of tiny water droplets or ice crystals.",
        "A rainbow appears when sunlight passes through water droplets.",
        "Thunder is the sound made by lightning.",
    ],
    "The human body": [
        "The heart pumps blood around the body.",
        "The lungs bring oxygen into the body.",
        "Bones give the body shape and protect organs.",
        "Sleep helps the body and brain rest and grow.",
    ],
    "Forces and motion": [
        "Gravity pulls objects toward Earth.",
        "A push or a pull can change how an object moves.",
        "Friction slows moving objects down.",
        "Magnets attract some metals such as iron.",
    ],
    "Light and sound": [
        "Light travels in straight lines.",
        "A shadow forms when an object blocks light.",
        "Sound is made by vibrations.",
        "Sound needs something to travel through, such as air or water.",
    ],
    "Ecosystems": [
        "Living things in an ecosystem depend on each other.",
        "A food chain shows what eats what.",
        "Decomposers such as fungi return nutrients to the soil.",
        "Trees take in carbon dioxide and release oxygen.",
    ],
    "Inventions and technology": [
        "A wheel reduces the effort needed to move heavy things.",
        "A lever helps lift a load with less force.",
        "Electricity flows in a closed circuit.",
        "A computer follows instructions written by people.",
    ],
    "Robots and AI": [
        "A robot is a machine that can sense, decide by following instructions, and act.",
        "Robots follow programs written by people.",
        "AI systems learn patterns from many examples.",
        "AI can make mistakes, so people check its work.",
    ],
    "Space exploration": [
        "Astronauts float in orbit because they are in continuous free fall around Earth.",
        "Rockets push hot gas backward to move forward.",
        "A satellite is an object that orbits a planet.",
        "There is no air to breathe in space.",
    ],
    "Drones and flight": [
        "Wings create lift when air moves over them.",
        "A drone uses spinning propellers to push air down and lift itself.",
        "Birds have hollow bones that keep them light.",
        "Pilots and drone operators check the weather before flying.",
    ],
    "Caring for the planet": [
        "Recycling turns used materials into new things.",
        "Solar panels turn sunlight into electricity.",
        "Saving water and energy helps protect nature.",
        "Litter can harm animals.",
    ],
}

# --------------------------------------------------------------------------
# Moneyfox: financial literacy, roughly ages 6-14.
# --------------------------------------------------------------------------
MONEY_TOPICS = {
    "What money is": {"min_age": 6, "concepts": [
        "Money is a tool people use to trade for things.",
        "Coins and notes have different values.",
        "People earn money by doing work that helps others."]},
    "Needs and wants": {"min_age": 6, "concepts": [
        "A need is something we must have to live safely, such as food and a home.",
        "A want is something nice to have but not necessary.",
        "Choosing one thing can mean waiting for another."]},
    "Saving for a goal": {"min_age": 6, "concepts": [
        "Saving means keeping some money for later.",
        "A goal and small regular steps make saving easier.",
        "Waiting patiently can make a bigger goal possible."]},
    "Spending wisely": {"min_age": 7, "concepts": [
        "Comparing prices helps to choose well.",
        "Money spent on one thing cannot be spent on another.",
        "It is fine to stop and think before buying."]},
    "Earning": {"min_age": 7, "concepts": [
        "People earn money for work, skills and time.",
        "Different jobs solve different problems for other people.",
        "Doing a job carefully builds trust."]},
    "Budgeting": {"min_age": 9, "concepts": [
        "A budget is a plan for money coming in and going out.",
        "A simple budget can have three parts: spend, save and share.",
        "A plan can change when something unexpected happens."]},
    "Value and price": {"min_age": 9, "concepts": [
        "Price is what you pay; value is how useful or important something is to you.",
        "Rare or hard-to-make things often cost more.",
        "Advertising tries to make people want things."]},
    "Sharing and giving": {"min_age": 6, "concepts": [
        "Sharing money or time can help other people.",
        "Giving is a choice, not something to feel forced into.",
        "Small gifts can matter a lot."]},
    "Starting a small business": {"min_age": 10, "concepts": [
        "A business sells something people need or want.",
        "Costs are what you spend; profit is what remains after costs.",
        "Listening to customers helps a business improve."]},
    "First steps in investing": {"min_age": 12, "concepts": [
        "Investing means putting money to work in the hope that it grows over time.",
        "Every investment carries risk, and money can be lost.",
        "Spreading money across different things lowers risk.",
        "Interest is money paid for the use of money."]},
}

# --------------------------------------------------------------------------
# Groa learning journeys: ordered steps, one objective per episode.
# --------------------------------------------------------------------------
GROA_JOURNEYS = {
    "Reading Rocket": {"domain": "reading", "steps": [
        "Notice the first sound of a word",
        "Recognise a word that repeats",
        "Read a short sentence together",
        "Guess a new word from the picture and the sentence",
        "Retell what happened first, next and last",
        "Read a whole page alone and say what it was about"]},
    "Number Trail": {"domain": "numeracy", "steps": [
        "Count objects up to ten",
        "Compare more and fewer",
        "Share things equally between friends",
        "Add two small groups together",
        "Spot and continue a pattern",
        "Measure something with steps or hands"]},
    "Little Scientist": {"domain": "science", "steps": [
        "Ask a question about something you see",
        "Make a guess about what will happen",
        "Try a simple test and watch closely",
        "Notice what changed and what stayed the same",
        "Explain what you found to a friend",
        "Ask the next question"]},
    "Kind Heart": {"domain": "emotions", "steps": [
        "Name a feeling",
        "Notice how someone else feels",
        "Take a calm breath when a feeling is big",
        "Ask for help with words",
        "Say sorry and make things right",
        "Include someone who is left out"]},
    "Brave Thinker": {"domain": "thinking", "steps": [
        "Tell the difference between a fact and an opinion",
        "Look for a second way to solve a problem",
        "Check whether something is true before repeating it",
        "Break a big problem into small steps",
        "Learn from a mistake",
        "Explain your reasons"]},
    "Future Makers": {"domain": "world", "steps": [
        "Meet someone who builds things: an engineer",
        "Meet someone who cares for others: a nurse or doctor",
        "Meet someone who teaches a robot: a programmer",
        "Meet someone who protects nature: an ecologist",
        "Meet someone who flies drones to help farmers",
        "Meet someone who designs things people use every day"]},
}

# --------------------------------------------------------------------------
# Modern professions for career exploration (no steering toward a career).
# --------------------------------------------------------------------------
PROFESSIONS = [
    "robotics engineer", "nurse", "marine biologist", "drone pilot", "software developer",
    "ecologist", "architect", "veterinarian", "teacher", "firefighter", "chef",
    "astronaut", "sound designer", "farmer", "product designer", "data scientist",
    "paramedic", "translator", "electrician", "weather forecaster", "game designer",
    "physical therapist", "solar panel technician", "librarian", "AI safety researcher",
]

# --------------------------------------------------------------------------
# Morals / values cards.
# --------------------------------------------------------------------------
MORALS = {
    "Honesty": "A character chooses to tell the truth even though it is a little hard, and trust grows.",
    "Empathy": "A character notices how someone else feels and responds with care.",
    "Courage": "A character feels unsure and takes one small, freely chosen step anyway.",
    "Responsibility": "A character takes care of a task or a promise and puts a mistake right.",
    "Kindness": "A small kind act changes someone's day.",
    "Patience": "Waiting and trying again leads somewhere good.",
    "Teamwork": "Different strengths solve a problem together.",
    "Curiosity": "A good question opens a new discovery.",
    "Gratitude": "A character notices something good and says thank you.",
}

# --------------------------------------------------------------------------
# Real-life support scenarios. These are story briefs, not therapy.
# --------------------------------------------------------------------------
SUPPORT_SCENARIOS = {
    "Starting school": "Show the first day step by step: arriving, meeting the teacher, finding a place, one friendly moment, going home. Name mixed feelings as normal.",
    "Visiting the doctor": "Show what happens at a check-up in order. The adult stays close. The doctor explains before touching. Do not promise it never hurts; say it is quick and people help.",
    "Going to the dentist": "Show the chair, the light, the small mirror and counting teeth. The child may raise a hand to pause. Keep it calm and factual.",
    "A stay in hospital": "Show the room, the kind staff, a familiar toy, and visits from family. Explain that hospitals help bodies get better. Never describe procedures in detail.",
    "Moving to a new home": "Show packing a special box, saying goodbye, the journey, and finding one good thing in the new place. Old friends are still friends.",
    "Parents living apart": "Both parents still love the child. It is not the child's fault. Show two homes with something familiar in each. Never blame either parent.",
    "A new baby in the family": "Show the baby needing lots of care, the older child's mixed feelings, a special job for the older child, and one-to-one time with a parent.",
    "Losing a pet": "Use clear, gentle words: the pet died and will not come back. Sadness is love. Show remembering through a drawing or a planted flower. No frightening detail.",
    "When someone is unkind": "Show a child being teased, telling a trusted adult, and adults acting. It is never the child's fault. Do not show revenge or physical fighting.",
    "Trouble with a friend": "Show a disagreement, a pause to calm down, listening to each other, and one way to repair. Friends can disagree and still be friends.",
    "Afraid of the dark": "Explore the dark at the child's own pace with a small light. Show that familiar things are still there. Never force, never mock, never promise the fear will vanish.",
    "Afraid of spiders": "Observe a small spider from a safe distance and learn one true fact. The child chooses how close to be. No pressure to touch.",
    "Big feelings": "Show a big feeling arriving, naming it, a slow breath, and asking for a hug or space. All feelings are allowed; hurting others is not.",
    "Wearing glasses": "Glasses are simply a useful tool that makes the world sharp. Show choosing frames and noticing new details. No teasing storyline is required.",
    "Getting braces": "Braces slowly help teeth line up. Show the first day feeling strange, soft food, and a friend who has them too.",
    "Being different": "Every character has something that makes them themselves. Show difference as ordinary and valuable, without turning it into a lesson about suffering.",
    "Making mistakes": "A character makes a mistake, feels bad, tells someone, and fixes or learns. Mistakes are how people learn.",
    "A new place": "Show looking around slowly, finding a safe spot, one friendly face, and one thing to look forward to.",
}

# Legacy support topic names used by v22 profiles.
SUPPORT_ALIASES = {
    "Spiders": "Afraid of spiders", "Darkness": "Afraid of the dark",
    "New places": "A new place", "Doctor visits": "Visiting the doctor",
}

# --------------------------------------------------------------------------
# Faith & Worldviews. The model writes an ORIGINAL family story and never
# quotes scripture. `references` are passages the parent may read from the
# family's own edition. They are pointers, not generated text, and have not
# been reviewed by a representative of each tradition.
# --------------------------------------------------------------------------
FAITH_POLICIES = {
    "Christianity": {
        "rule": "Use an original parable about kindness. A simple lamp, olive branch, or cross may appear. Do not quote scripture or depict God.",
        "references": [
            {"ref": "Luke 10:25–37", "about": "The Good Samaritan: helping a stranger"},
            {"ref": "Luke 6:31", "about": "Treating others as you wish to be treated"},
            {"ref": "Matthew 7:12", "about": "The Golden Rule"},
        ]},
    "Judaism": {
        "rule": "Use an original family story about kindness and gratitude. Shabbat candles, challah, or a simple Star of David may appear. Never write or depict a divine name.",
        "references": [
            {"ref": "Leviticus 19:18", "about": "Loving your neighbour"},
            {"ref": "Micah 6:8", "about": "Justice, kindness and humility"},
            {"ref": "Pirkei Avot 1:2", "about": "The world stands on Torah, service and acts of kindness"},
        ]},
    "Islam": {
        "rule": "Use an original family story about mercy and generosity. Use geometric patterns, a lantern, crescent, or mosque silhouette. Never depict Allah, Muhammad, prophets, or sacred text.",
        "references": [
            {"ref": "Qur'an 2:177", "about": "Righteousness includes giving to those in need"},
            {"ref": "Qur'an 93:9–10", "about": "Kindness to the orphan and to the one who asks"},
            {"ref": "Qur'an 49:13", "about": "People were made different so they may know one another"},
        ]},
    "Buddhism": {
        "rule": "Use an original story about compassion and mindful attention. A lotus, Dharma wheel, or peaceful garden may appear. Do not claim a single universal doctrine.",
        "references": [
            {"ref": "Dhammapada 5", "about": "Hatred is not ended by hatred"},
            {"ref": "Karaniya Metta Sutta (Sutta Nipata 1.8)", "about": "Loving-kindness toward all beings"},
            {"ref": "Dhammapada 223", "about": "Meeting anger with calm"},
        ]},
    "Hinduism": {
        "rule": "Use an original family story about duty, kindness, and gratitude. A diya, lotus, or rangoli may appear. Do not depict deities or quote sacred text.",
        "references": [
            {"ref": "Bhagavad Gita 12:13–14", "about": "Being friendly and compassionate to all"},
            {"ref": "Taittiriya Upanishad 1.11", "about": "Honouring mother, father, teacher and guest"},
        ]},
    "Humanism": {
        "rule": "Use an original story about kindness, fairness and curiosity grounded in human care and reason. Do not criticise any religion and do not present a worldview as scientific proof.",
        "references": []},
}

PACKS = ("story", "science", "faith", "money", "groa", "support", "profession")


def reading_stage(value, legacy_level: str = "") -> int:
    """Clamp an explicit stage or map a legacy three-level setting."""
    if isinstance(value, bool):
        value = None
    if isinstance(value, (int, float)) and 1 <= int(value) <= 8:
        return int(value)
    return LEGACY_READING_LEVELS.get(legacy_level, 3)


def companion_for(key: str | None, seed: int) -> dict:
    for companion in COMPANIONS:
        if companion["key"] == key:
            return companion
    return COMPANIONS[seed % len(COMPANIONS)]


def hero_scene_plan(page_total: int) -> list[bool]:
    """First page: recognisable portrait. One or two key scenes include the child.

    Every other illustration follows the page itself and does not force the hero in.
    """
    plan = [False] * page_total
    if page_total <= 0:
        return plan
    plan[0] = True
    plan[page_total - 1] = True
    if page_total >= 6:
        plan[round(page_total * 0.6) - 1] = True
    return plan
