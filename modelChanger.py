from aqt import mw
from aqt import changenotetype
from anki.hooks import wrap
from aqt.qt import *
from aqt.utils import askUser
from aqt.forms import changemodel

def addLanguageModels():
    if not hasattr(mw, "addonLanguageModels"):
        mw.addonLanguageModels = {}
    mw.addonLanguageModels["Japanese Sentence"] = { "valid-targets" : [
    "Japanese Sentence", 
    "Japanese Vocabulary", 
    "Japanese Audio Sentence", 
    "Japanese Audio Vocabulary"
    ],
    "fields" : ['Target Word', 'Sentence', 'Translation', 'Definitions', 'Image', 'Sentence Audio', 'Word Audio']
    }
    mw.addonLanguageModels["Japanese Vocabulary"] = { "valid-targets" : [
    "Japanese Sentence", 
    "Japanese Vocabulary", 
    "Japanese Audio Sentence", 
    "Japanese Audio Vocabulary"
    ],
    "fields" : ['Target Word', 'Sentence', 'Translation', 'Definitions', 'Image', 'Sentence Audio', 'Word Audio']
    }
    mw.addonLanguageModels["Japanese Audio Sentence"] = { "valid-targets" : [
    "Japanese Sentence", 
    "Japanese Vocabulary", 
    "Japanese Audio Sentence", 
    "Japanese Audio Vocabulary"
    ],
    "fields" : ['Target Word', 'Sentence', 'Translation', 'Definitions', 'Image', 'Sentence Audio', 'Word Audio']
    }
    mw.addonLanguageModels["Japanese Audio Vocabulary"] = { "valid-targets" :  [
    "Japanese Sentence", 
    "Japanese Vocabulary", 
    "Japanese Audio Sentence", 
    "Japanese Audio Vocabulary"
    ],
    "fields" : ['Target Word', 'Sentence', 'Translation', 'Definitions', 'Image', 'Sentence Audio', 'Word Audio']
    }


addLanguageModels()

def addonRebuildTemplateMap(self, key=None, attr=None):
    print("called addonRebuildTemplateMap")
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


def addonModelChanged(self, model):
    print("called addonModelChanged")

    self.changeBetweenAddonNoteTypes = False
    self.targetModel = model
    predeterminedTemplateAndFieldMap = changeIsBetweenValidJPNoteTypes(self.oldModel, self.targetModel)
    if predeterminedTemplateAndFieldMap:
        self.changeBetweenAddonNoteTypes = predeterminedTemplateAndFieldMap
        if not hasattr(self, "addonLabels") or not self.addonLabels:
            replaceTemplateMap(self)
    else:
        maybeRemoveJPLabel(self)
        self.rebuildTemplateMap()
        self.rebuildFieldMap()

def getFieldNameList(fieldData):
    print("called getFieldNameList")

    return [field['name'] for field in fieldData]

def fieldsAreTheSameAsTheDefault(testedNoteType, addonNoteType):
    print("called fieldsAreTheSameAsTheDefault")

    testedFields = getFieldNameList(testedNoteType["flds"])
    addonFields = addonNoteType["fields"]
    fieldsThatDontOccurInBoth = list(set(addonFields)^set(testedFields))
    if len(fieldsThatDontOccurInBoth) == 0:
        return True
    return False

def changeIsBetweenValidJPNoteTypes(originalNoteType, targetNoteType):
    print("called changeIsBetweenValidJPNoteTypes")

    if originalNoteType["name"] in mw.addonLanguageModels.keys():
        originJPNoteType = mw.addonLanguageModels[originalNoteType["name"]]
        if onlyOneCardTypeInNoteType(originalNoteType) and fieldsAreTheSameAsTheDefault(originalNoteType, originJPNoteType):
            if targetNoteType["name"] in originJPNoteType["valid-targets"]:
                destinationJPNoteType = mw.addonLanguageModels[targetNoteType["name"]]
                if onlyOneCardTypeInNoteType(targetNoteType) and fieldsAreTheSameAsTheDefault(targetNoteType, destinationJPNoteType):
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

def maybeRemoveJPLabel(self):
    print("called maybeRemoveJPLabel")

    if hasattr(self, "addonLabels") and self.addonLabels:
        keys = ["t", "f"]
        for key in keys:
            lay = getattr(self, key + "layout")
            lay.removeWidget(self.addonLabels[key])
            self.addonLabels[key].deleteLater()
    self.addonLabels = False   



def replaceTemplateMap(self):
    print("called replaceTemplateMap")

    self.addonLabels = {}
    keys = ["t", "f"]
    for key in keys:
        map = getattr(self, key + "widg")
        lay = getattr(self, key + "layout")
        self.addonLabels[key] = QLabel('JP will automatically convert between these Note Types\nfor you. Simply press the "OK" button to proceed.')
        lay.addWidget(self.addonLabels[key])
        if map:
            lay.removeWidget(map)
            map.deleteLater()
            setattr(self, key + "MapWidget", None)

def addonAccent(self):
    # check maps
    if hasattr(self, "changeBetweenAddonNoteTypes") and self.changeBetweenAddonNoteTypes is not False:
        cmap, fmap = self.changeBetweenAddonNoteTypes
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


if not hasattr(changemodel, "addonOveriddenMethods"):
    print("ADDED THROUGH JP")
    changemodel.addonOveriddenMethods = True
    changemodel.accept = addonAccent
    changemodel.modelChanged = addonModelChanged
    changemodel.rebuildTemplateMap = addonRebuildTemplateMap