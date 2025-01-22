from aqt import mw
from aqt import changenotetype
from anki.hooks import wrap
from aqt.qt import *
from aqt.utils import askUser
from aqt.forms import changemodel

def addLanguageModels():
    if not hasattr(mw, "misoLanguageModels"):
        mw.misoLanguageModels = {}
    mw.misoLanguageModels["Miso Japanese Sentence"] = { "valid-targets" : [
    "Miso Japanese Sentence", 
    "Miso Japanese Vocabulary", 
    "Miso Japanese Audio Sentence", 
    "Miso Japanese Audio Vocabulary"
    ],
    "fields" : ['Target Word', 'Sentence', 'Translation', 'Definitions', 'Image', 'Sentence Audio', 'Word Audio']
    }
    mw.misoLanguageModels["Miso Japanese Vocabulary"] = { "valid-targets" : [
    "Miso Japanese Sentence", 
    "Miso Japanese Vocabulary", 
    "Miso Japanese Audio Sentence", 
    "Miso Japanese Audio Vocabulary"
    ],
    "fields" : ['Target Word', 'Sentence', 'Translation', 'Definitions', 'Image', 'Sentence Audio', 'Word Audio']
    }
    mw.misoLanguageModels["Miso Japanese Audio Sentence"] = { "valid-targets" : [
    "Miso Japanese Sentence", 
    "Miso Japanese Vocabulary", 
    "Miso Japanese Audio Sentence", 
    "Miso Japanese Audio Vocabulary"
    ],
    "fields" : ['Target Word', 'Sentence', 'Translation', 'Definitions', 'Image', 'Sentence Audio', 'Word Audio']
    }
    mw.misoLanguageModels["Miso Japanese Audio Vocabulary"] = { "valid-targets" :  [
    "Miso Japanese Sentence", 
    "Miso Japanese Vocabulary", 
    "Miso Japanese Audio Sentence", 
    "Miso Japanese Audio Vocabulary"
    ],
    "fields" : ['Target Word', 'Sentence', 'Translation', 'Definitions', 'Image', 'Sentence Audio', 'Word Audio']
    }


addLanguageModels()

def misoRebuildTemplateMap(self, key=None, attr=None):
    print("called misoRebuildTemplateMap")
    if not key:
        key = "t"
        attr = "tmpls"
    map = getattr(self, key + "widg")
    lay = getattr(self, key + "layout")
    src = self.oldModel[attr]
    dst = self.targetModel[attr]
    if map:
        try:
            lay.removeWidget(map)
            map.deleteLater()
            setattr(self, key + "MapWidget", None)
        except:
            pass
    map = QWidget()
    l = QGridLayout()
    combos = []
    targets = [x["name"] for x in dst] + [_("Nothing")]
    indices = {}
    for i, x in enumerate(src):
        l.addWidget(QLabel(_("Change %s to:") % x["name"]), i, 0)
        cb = QComboBox()
        cb.addItems(targets)
        idx = min(i, len(targets) - 1)
        cb.setCurrentIndex(idx)
        indices[cb] = idx
        qconnect(
            cb.currentIndexChanged,
            lambda i, cb=cb, key=key: self.onComboChanged(i, cb, key),
        )
        combos.append(cb)
        l.addWidget(cb, i, 1)
    map.setLayout(l)
    lay.addWidget(map)
    setattr(self, key + "widg", map)
    setattr(self, key + "layout", lay)
    setattr(self, key + "combos", combos)
    setattr(self, key + "indices", indices)


def misoModelChanged(self, model):
    print("called misoModelChanged")

    self.changeBetweenMisoNoteTypes = False
    self.targetModel = model
    predeterminedTemplateAndFieldMap = changeIsBetweenValidMisoNoteTypes(self.oldModel, self.targetModel)
    if predeterminedTemplateAndFieldMap:
        self.changeBetweenMisoNoteTypes = predeterminedTemplateAndFieldMap
        if not hasattr(self, "misoLabels") or not self.misoLabels:
            replaceTemplateMap(self)
    else:
        maybeRemoveMisoLabel(self)
        self.rebuildTemplateMap()
        self.rebuildFieldMap()

def getFieldNameList(fieldData):
    print("called getFieldNameList")

    return [field['name'] for field in fieldData]

def fieldsAreTheSameAsTheDefault(testedNoteType, misoNoteType):
    print("called fieldsAreTheSameAsTheDefault")

    testedFields = getFieldNameList(testedNoteType["flds"])
    misoFields = misoNoteType["fields"]
    fieldsThatDontOccurInBoth = list(set(misoFields)^set(testedFields))
    if len(fieldsThatDontOccurInBoth) == 0:
        return True
    return False

def changeIsBetweenValidMisoNoteTypes(originalNoteType, targetNoteType):
    print("called changeIsBetweenValidMisoNoteTypes")

    if originalNoteType["name"] in mw.misoLanguageModels.keys():
        originMisoNoteType = mw.misoLanguageModels[originalNoteType["name"]]
        if onlyOneCardTypeInNoteType(originalNoteType) and fieldsAreTheSameAsTheDefault(originalNoteType, originMisoNoteType):
            if targetNoteType["name"] in originMisoNoteType["valid-targets"]:
                destinationMisoNoteType = mw.misoLanguageModels[targetNoteType["name"]]
                if onlyOneCardTypeInNoteType(targetNoteType) and fieldsAreTheSameAsTheDefault(targetNoteType, destinationMisoNoteType):
                    fieldMap = generateFieldOrdinateMap(originalNoteType, targetNoteType)
                    templateMap = {0 : 0}
                    return [templateMap, fieldMap]
    return False

def onlyOneCardTypeInNoteType(noteType):
    print("called onlyOneCardTypeInNoteType")

    if len(noteType["tmpls"]) == 1:
        return True
    return False

def generateFieldOrdinateMap(originalNoteType, targetNoteType):
    print("called generateFieldOrdinateMap")

    ogFields = originalNoteType["flds"]
    tFields = targetNoteType["flds"]
    fieldMap = {}
    for ogf in ogFields:
        ordinal = ogf["ord"]
        name = ogf["name"]
        targetOrdinal = getOrdinalForName(name, tFields)
        fieldMap[ordinal] = targetOrdinal
    return fieldMap 

def getOrdinalForName(name, fields):
    print("called getOrdinalForName")

    for field in fields:
        if field["name"] == name:
            return field["ord"]

{'name': 'Sentence', 'ord': 0, 'sticky': False, 'rtl': False, 'font': 'Arial', 'size': 20}

def maybeRemoveMisoLabel(self):
    print("called maybeRemoveMisoLabel")

    if hasattr(self, "misoLabels") and self.misoLabels:
        keys = ["t", "f"]
        for key in keys:
            lay = getattr(self, key + "layout")
            lay.removeWidget(self.misoLabels[key])
            self.misoLabels[key].deleteLater()
    self.misoLabels = False   



def replaceTemplateMap(self):
    print("called replaceTemplateMap")

    self.misoLabels = {}
    keys = ["t", "f"]
    for key in keys:
        map = getattr(self, key + "widg")
        lay = getattr(self, key + "layout")
        self.misoLabels[key] = QLabel('Miso will automatically convert between these Note Types\nfor you. Simply press the "OK" button to proceed.')
        lay.addWidget(self.misoLabels[key])
        if map:
            lay.removeWidget(map)
            map.deleteLater()
            setattr(self, key + "MapWidget", None)

def misoAccept(self):
    # check maps
    if hasattr(self, "changeBetweenMisoNoteTypes") and self.changeBetweenMisoNoteTypes is not False:
        cmap, fmap = self.changeBetweenMisoNoteTypes
    else:
        fmap = self.getFieldMap()
        cmap = self.getTemplateMap()
    if any(True for c in list(cmap.values()) if c is None):
        if not askUser(
                _(
                    """\
Any cards mapped to nothing will be deleted. \
If a note has no remaining cards, it will be lost. \
Are you sure you want to continue?"""
                )
        ):
            return
    self.browser.mw.checkpoint(_("Change Note Type"))
    b = self.browser
    b.mw.col.modSchema(check=True)
    b.mw.progress.start()
    b.note_type.beginReset()
    mm = b.mw.col.note_types
    mm.change(self.oldModel, self.nids, self.targetModel, fmap, cmap)
    b.search()
    b.note_type.endReset()
    b.mw.progress.finish()
    b.mw.reset()
    self.cleanup()
    QDialog.accept(self)


if not hasattr(changemodel, "misoOveriddenMethods"):
    print("ADDED THROUGH JP")
    changemodel.misoOveriddenMethods = True
    changemodel.accept = misoAccept
    changemodel.modelChanged = misoModelChanged
    changemodel.rebuildTemplateMap = misoRebuildTemplateMap