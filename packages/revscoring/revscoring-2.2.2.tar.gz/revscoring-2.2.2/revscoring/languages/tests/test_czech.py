import pickle


from .. import czech
from ...datasources import revision_oriented
from ...dependencies import solve
from .util import compare_extraction

BAD = [
    "arnulfo",
    "blb",
    "blbá",
    "blbec",
    "blbej",
    "blbost",
    "blbosti",
    "buzerant",
    "buzeranti",
    "buzik",
    "buzna",
    "buzny",
    "curaci",
    "curak",
    "čumíš",
    "čuráci",
    "čůráci",
    "čurak",
    "čurák",
    "čůrák",
    "čuráka",
    "ddd",
    "dddd",
    "ddddd",
    "debil",
    "debile",
    "debilní",
    "debilové",
    "debilů",
    "dementi",
    "děvka",
    "ekrimi",
    "eskader",
    "exkrementu",
    "fekaliemi",
    "fekalni",
    "freeforfun",
    "fuck",
    "fuj",
    "gay",
    "gej",
    "gportal",
    "hnusná",
    "hovada",
    "hovadina",
    "hoven",
    "hovna",
    "hovno",
    "hovnu",
    "howno",
    "idiot",
    "kastrováni",
    "keci",
    "kokot",
    "kokota",
    "kokote",
    "kokoti",
    "kokotina",
    "kravina",
    "kreten",
    "kretén",
    "kreteni",
    "kreténi",
    "kunda",
    "kundo",
    "kundy",
    "kurva",
    "kurvy",
    "kuzdasová",
    "magor",
    "mrdá",
    "mrdal",
    "mrdání",
    "mrdat",
    "mrdka",
    "mrdky",
    "nasrat",
    "necum",
    "nečum",
    "neser",
    "nesmrděli",
    "penis",
    "penisu",
    "péra",
    "péro",
    "pica",
    "pice",
    "pici",
    "pico",
    "picovina",
    "picu",
    "piča",
    "píča",
    "piče",
    "píče",
    "piči",
    "píči",
    "pičo",
    "píčo",
    "pičovina",
    "píčovina",
    "píčoviny",
    "piču",
    "píču",
    "pičus",
    "píčus",
    "polib",
    "polibte",
    "posral",
    "posrávání",
    "prd",
    "prdel",
    "prdele",
    "prdeli",
    "prdy",
    "sex",
    "sexy",
    "slovackatiskovakancelar",
    "smrad",
    "smrděl",
    "smrdi",
    "smrdí",
    "smrdis",
    "smrdíš",
    "smrdite",
    "smrdíte",
    "sracka",
    "sraček",
    "sračka",
    "sračky",
    "sraní",
    "svině",
    "šuká",
    "šukal",
    "šukání",
    "šukat",
    "teplej",
    "vole",
    "všiví",
    "vycucali",
    "vykaly",
    "zasranej",
    "zasraný",
    "zkurvenýho",
    "zmrd",
    "zmrde",
    "zmrdi"
]

INFORMAL = [
    "ahoj",
    "ahojky",
    "balustrada",
    "bla",
    "blablabla",
    "borec",
    "bydlí",
    "cau",
    "čau",
    "čus",
    "děkuji",
    "dete",
    "děte",
    "editovat",
    "furt",
    "haha",
    "hahaha",
    "hahahaha",
    "hodne",
    "jeto",
    "jjj",
    "jste",
    "julieta",
    "juliin",
    "kapuletů",
    "kolínšti",
    "kterej",
    "kurzíva",
    "lol",
    "mam",
    "mám",
    "mate",
    "máte",
    "média",
    "miluju",
    "moje",
    "montekové",
    "monteků",
    "mucednici",
    "nadpisu",
    "neformátovaný",
    "neni",
    "neprůstřelné",
    "nepřestanete",
    "nevim",
    "nuda",
    "odkazu",
    "omg",
    "omluvného",
    "patláním",
    "pekna",
    "pěkně",
    "pepa",
    "plnýho",
    "podžezali",
    "porno",
    "prografika",
    "proste",
    "prostě",
    "protoze",
    "přeškrtnutý",
    "příklad",
    "příspěvky",
    "rád",
    "roméo",
    "romerovi",
    "romeus",
    "salvadorský",
    "salvadorští",
    "sem",
    "smazat",
    "sou",
    "ste",
    "strašně",
    "tady",
    "taky",
    "tipynavylety",
    "tučný",
    "tybalt",
    "tybalta",
    "uklizečky",
    "ukradnou",
    "vam",
    "vám",
    "vás",
    "velkej",
    "velky",
    "vložit",
    "vložte",
    "vytrznik",
    "zdar",
    "znecistuje",
    "znečistil"
]

OTHER = [
    """
    Rúmí se narodil v Balchu (město v tehdejší Persii, v provincii
    Chorásánu, nyní v severním Afghánistánu) a zemřel v Konyi (v Anatolii,
    tehdy Rúmský sultanát, dnes Turecko), kam se roku 1228 přestěhoval na
    předchozí pozvání rúmského sultána Kajkubáda I. Svou poezii psal v
    perštině a jeho práce jsou široce čtené v Íránu a Afghánistánu, kde
    se perštinou mluví.
    """
]


def test_badwords():
    compare_extraction(czech.badwords.revision.datasources.matches, BAD,
                       OTHER)

    assert czech.badwords == pickle.loads(pickle.dumps(czech.badwords))


def test_informals():
    compare_extraction(czech.informals.revision.datasources.matches,
                       INFORMAL, OTHER)

    assert czech.informals == pickle.loads(pickle.dumps(czech.informals))


def test_dictionary():
    cache = {revision_oriented.revision.text: 'kam se roku worngly.'}
    assert (solve(czech.dictionary.revision.datasources.dict_words, cache=cache) ==
            ["kam", "se", "roku"])
    assert (solve(czech.dictionary.revision.datasources.non_dict_words,
                  cache=cache) ==
            ["worngly"])

    assert czech.dictionary == pickle.loads(pickle.dumps(czech.dictionary))


def test_stopwords():
    cache = {revision_oriented.revision.text: 'rúmského sultána odkazy'}
    assert (solve(czech.stopwords.revision.datasources.stopwords, cache=cache) ==
            ['odkazy'])
    assert (solve(czech.stopwords.revision.datasources.non_stopwords,
                  cache=cache) ==
            ['rúmského', 'sultána'])

    assert czech.stopwords == pickle.loads(pickle.dumps(czech.stopwords))
