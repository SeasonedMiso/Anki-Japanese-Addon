# -*- coding: utf-8 -*-
from aqt.qt import *
import re
from .miutils import miInfo, miAsk
from os.path import join
from .constants import *

class MassExporter:
    def __init__(self, mw, exporter, addon_path):
        self.mw = mw
        self.exporter = exporter
        self.dictParser = self.exporter.dictParser
        self.addon_path = addon_path
        self.config = self.mw.addonManager.getConfig(__name__)
        if 'field_pairs' not in self.config:
            self.config['field_pairs'] = []
        if 'checkbox_states' not in self.config:
            self.config['checkbox_states'] = {
                'furigana': True,
                'dict_form': True,
                'accents': True,
                'audio': False,
                'graphs': False
            }
        self.mw.addonManager.writeConfig(__name__, self.config)

    def onRegenerate(self, browser):
        import anki.find
        notes = browser.selectedNotes()
        if notes:
            fields = anki.find.fieldNamesForNotes(self.mw.col, notes)
            generateWidget = QDialog(None, Qt.WindowType.Window)
            generateWidget.setWindowIcon(QIcon(join(self.addon_path, 'icons', 'miso.png')))
            layout = QVBoxLayout()

            # Field Pairs List
            self.fieldPairsList = QListWidget()
            self.fieldPairsList.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            self.updateFieldPairsList()
            layout.addWidget(self.fieldPairsList)

            # Add Field Pair Button
            addPairButton = QPushButton('Add Field Pair')
            addPairButton.clicked.connect(lambda: self.addFieldPair(fields))
            layout.addWidget(addPairButton)

            # Remove Field Pair Button
            removePairButton = QPushButton('Remove Selected Field Pair')
            removePairButton.clicked.connect(self.removeFieldPair)
            layout.addWidget(removePairButton)

            # Checkboxes
            self.b1 = QCheckBox("Furigana")
            self.b1.setChecked(self.config['checkbox_states']['furigana'])
            self.b2 = QCheckBox("Dict Form")
            self.b2.setChecked(self.config['checkbox_states']['dict_form'])
            self.b3 = QCheckBox("Accents")
            self.b3.setChecked(self.config['checkbox_states']['accents'])
            self.b4 = QCheckBox("Audio")
            self.b4.setChecked(self.config['checkbox_states']['audio'])
            self.b5 = QCheckBox("Graphs")
            self.b5.setChecked(self.config['checkbox_states']['graphs'])

            # Add checkboxes to layout
            layout.addWidget(self.b1)
            layout.addWidget(self.b2)
            layout.addWidget(self.b3)
            layout.addWidget(self.b4)
            layout.addWidget(self.b5)

            # Overwrite Combo Box
            addLabel = QLabel()
            addLabel.setText('Overwrite?:')
            addType = QComboBox()
            addType.addItems(['Overwrite', 'Add', 'If Empty'])
            layout.addWidget(addLabel)
            layout.addWidget(addType)

            # Execute Button
            b6 = QPushButton('Execute')

            # def massGenerate(self, furigana, dictform, accents, audio, charts, notes, generateWidget, addType):
            # 'dest' and 'addType'

            b6.clicked.connect(
                lambda: self.massGenerate(self.b1, self.b2, self.b3, self.b4, self.b5, notes, generateWidget, addType.currentText()))
            layout.addWidget(b6)

            # Set up the dialog
            generateWidget.setWindowTitle("Generate Accents And Furigana")
            generateWidget.setLayout(layout)
            generateWidget.exec()
        else:
            miInfo('Please select some cards before attempting to mass generate.', level='err')

    def updateFieldPairsList(self):
        self.fieldPairsList.clear()
        for pair in self.config['field_pairs']:
            self.fieldPairsList.addItem(f"{pair['input']} -> {pair['output']}")

    def addFieldPair(self, fields):
        dialog = QDialog()
        dialog.setWindowTitle("Add Field Pair")
        layout = QVBoxLayout()
        dialog.setLayout(layout)

        # Input Combo Box
        inputLabel = QLabel()
        inputLabel.setText('Input Field:')
        inputCombo = QComboBox()
        inputCombo.addItems(fields)
        layout.addWidget(inputLabel)
        layout.addWidget(inputCombo)

        # Output Combo Box
        outputLabel = QLabel()
        outputLabel.setText('Output Field:')
        outputCombo = QComboBox()
        outputCombo.addItems(fields)
        layout.addWidget(outputLabel)
        layout.addWidget(outputCombo)

        # Add Button
        addButton = QPushButton('Add')
        addButton.clicked.connect(lambda: self.saveFieldPair(inputCombo.currentText(), outputCombo.currentText(), dialog))
        layout.addWidget(addButton)

        dialog.exec()

    def saveFieldPair(self, inputField, outputField, dialog):
        self.config['field_pairs'].append({'input': inputField, 'output': outputField})
        self.mw.addonManager.writeConfig(__name__, self.config)
        self.updateFieldPairsList()
        dialog.close()

    def removeFieldPair(self):
        selectedItem = self.fieldPairsList.currentItem()
        if selectedItem:
            inputField, outputField = selectedItem.text().split(' -> ')
            self.config['field_pairs'] = [pair for pair in self.config['field_pairs'] if pair['input'] != inputField or pair['output'] != outputField]
            self.mw.addonManager.writeConfig(__name__, self.config)
            self.updateFieldPairsList()

    def massGenerate(self, furigana, dictform, accents, audio, charts, notes, generateWidget, addType):
        if not miAsk('Are you sure you want to generate for all selected field pairs?'):
            return

        # Save checkbox states to config
        self.config['checkbox_states'] = {
            'furigana': furigana.isChecked(),
            'dict_form': dictform.isChecked(),
            'accents': accents.isChecked(),
            'audio': audio.isChecked(),
            'graphs': charts.isChecked()
        }
        self.mw.addonManager.writeConfig(__name__, self.config)

        self.mw.checkpoint('Mass Accent Generation')
        generateWidget.close()
        progWid, bar = self.getProgressWidget()
        bar.setMinimum(0)
        bar.setMaximum(len(notes) * len(self.config['field_pairs']))
        val = 0
        for pair in self.config['field_pairs']:
            inputField = pair['input']
            outputField = pair['output']
            for nid in notes:
                note = self.mw.col.get_note(nid)
                fields = self.mw.col.models.fieldNames(note.model())
                if inputField in fields and outputField in fields:
                    text = note[inputField]
                    newText = text
                    text = text.replace('</div> <div>', '</div><div>')
                    htmlFinds, text = self.exporter.htmlRemove(text)
                    text, sounds = self.exporter.removeBrackets(text, True)
                    text = text.replace(',&', '-co-am-')
                    text, invalids = self.exporter.replaceInvalidChars(text)
                    text = self.mw.col.media.strip(text)
                    results = self.dictParser.getParsed(text)
                    results = self.exporter.wordData(results)
                    text, audioGraphList = self.dictParser.dictBasedParsing(results, newText, False, [
                        furigana.isChecked(), dictform.isChecked(), accents.isChecked(), audio.isChecked(), charts.isChecked()
                    ])
                    if htmlFinds:
                        text = self.exporter.replaceHTML(text, htmlFinds)
                    for match in sounds:
                        text = text.replace(AUDIO_REPLACER, match, 1)
                    if text:
                        text = self.exporter.returnInvalids(text, invalids)
                        text = text.replace('-co-am-', ',&').strip()
                        if addType == 'If Empty':
                            if note[outputField] == '':
                                note[outputField] = text
                        elif addType == 'Add':
                            if note[outputField] == '':
                                note[outputField] = text
                            else:
                                note[outputField] += '<br>' + text
                        else:
                            note[outputField] = self.exporter.convertMalformedSpaces(text)
                    if audioGraphList:
                        self.exporter.addVariants(audioGraphList, note)
                    if text or audioGraphList:
                        self.mw.col.update_note(note, skip_undo_entry=True)
                val += 1
                bar.setValue(val)
                self.mw.app.processEvents()
        self.mw.progress.finish()
        self.mw.reset()

    def getProgressWidget(self):
        progressWidget = QWidget(None)
        layout = QVBoxLayout()
        progressWidget.setFixedSize(400, 70)
        progressWidget.setWindowModality(Qt.WindowModality.ApplicationModal)
        progressWidget.setWindowTitle('Generating...')
        progressWidget.setWindowIcon(QIcon(join(self.addon_path, 'icons', 'miso.png')))
        bar = QProgressBar(progressWidget)
        if is_mac:
            bar.setFixedSize(380, 50)
        else:
            bar.setFixedSize(390, 50)
        bar.move(10,10)
        per = QLabel(bar)
        per.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progressWidget.show()
        return progressWidget, bar;

    def massRemove(self, field,  notes, generateWidget):
        if not miAsk('Are you sure you want to mass remove readings from the "'+ field +'" field? .'):
            return
        self.mw.checkpoint('Mass Accent Removal')
        generateWidget.close() 
        progWid, bar = self.getProgressWidget()   
        bar.setMinimum(0)
        bar.setMaximum(len(notes))
        val = 0;  
        for nid in notes:
            note = self.mw.col.get_note(nid)
            fields = self.mw.col.note_type.field_names(note.note_type())
            if field in fields:
                text = note[field] 
                text =  self.exporter.removeBrackets(text)
                note[field] = text
                self.mw.col.update_note(note, skip_undo_entry=True)
                # note.flush()
            val+=1;
            bar.setValue(val)
            self.mw.app.processEvents()
        self.mw.progress.finish()
        self.mw.reset()
