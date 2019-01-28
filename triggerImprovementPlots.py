
import ROOT
import re
import math
import json
from ROOT import TLorentzVector
from pprint import pprint

#Formatting purposes
#import morisotColorsAndMarkers as colorsAndMarkers
#from plottingWrapper import drawPlotsOverlaidAndTheirRatio

def main():

    ##Configurable variables
    ##manually re-name these for each new input .root files that you want to analyze
    path1 = "/home/bryan/work/TLA/TriggerImprovementStudies/01_22_triggerImprovements_singleJet_gsc_mu/singleJet/hist-filelist.root"
    efficiencyDictPath = "efficiencyPointsDict.json"
    plotTitle = "Jet pT(Lead) Single Jet Triggers"
    #outputPDF = "TriggerImprovements_2017_singleJet_allTriggers_10_10"
    outputPDF = "TriggerImprovements_2017_singleJet_individualTriggers_01_28"
    ##Formatting- change these if needed
    setLogX = True
    setLogY = False

    ##Read in efficiency points from json
    ##When there are different probe collections for each reference collection, use the higher threshold reference collection
    namesAndEffs = {}
    with open(efficiencyDictPath) as f:
        effDict = json.load(f)

    for key1 in effDict.keys():
        #print key1
        #print(effDict[key1])
        tempProbe1 = key1.split('-', 1)[0]
        tempRef1 = key1.rsplit('-', 1)[1]
        #print key1.split('-', 1)
        #print "probe jet: ", tempProbe1
        #print "ref jet: ", tempRef1
        tempRefThreshold1 = tempRef1.split('j', 1)[-1].split('_L1', 1)[0]
        #namesAndEffs[tempProbe1] = effDict[key1]
        #print tempRefThreshold1
        for key2 in effDict.keys():
            tempProbe2 = key2.split('-', 1)[0]
            tempRef2 = key2.rsplit('-', 1)[1]
            tempRefThreshold2 = tempRef2.split('j', 1)[-1].split('_L1', 1)[0]
            #print "threshold 1: ", float(tempRefThreshold1), " threshold 2: ", float(tempRefThreshold2)
            if ((tempProbe2 == tempProbe1) and (float(tempRefThreshold2) > float(tempRefThreshold1))):
                namesAndEffs[tempProbe1] = effDict[key2]
        #print namesAndEffs
    
    TFile1 = ROOT.TFile(path1)

    histList = []
    histNames = []
    legendLabels = []
    #goodColors = [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 28, 30, 35, 38, 39, 41, 42, 46, 49] #20 distinctive colors.  If more than 20 plots things need to be re-though, including putting 20 plots on one canvas...
    goodColors = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27,  28, 29, 30, 35, 38, 39, 41, 42, 46, 49]
    stack = ROOT.THStack("hStack", plotTitle) 

    ##get leading pT histograms from .root file
    for h in TFile1.GetListOfKeys():
        h = h.ReadObj()
        if "h_PtLeadingReference_" in h.GetName():
            histList.append(TFile1.Get(h.GetName()))

    ##sort the histogram list by max value in the histogram.
    ##This allows the first histogram in the list to automatically set a y-axis that ensures all plots will be visible on the canvas         
    histList.sort(reverse=True, key=getMax)
    for hists in histList:
        histNames.append(hists.GetName())
        legendLabels.append(hists.GetName().replace('h_PtLeadingReference_',''))
        
    ##Draw histograms and label legend entries as trigger names
    for i,hist in enumerate(histList):
        if getMax(hist) == 0:
            continue
        if i == 0:
            TriggerCanvas = ROOT.TCanvas("cTriggers","2017 Leading pT")
            if setLogX is True:
                TriggerCanvas.SetLogx()
            if setLogY is True:
                TriggerCanvas.SetLogy()
            legend = ROOT.TLegend(0.825224,0.435737,0.979478,0.917304)
            legend.AddEntry(hist,legendLabels[i],"l")
            hist.SetTitle(plotTitle)
            hist.GetXaxis().SetTitle("p_{T, Lead} [GeV]")
            hist.GetYaxis().SetTitle("Number of Recorded Entries")
            hist.SetLineColor(goodColors[i])
            hist.SetStats(False)
            hist.Draw("hist")
            #stack.Add(hist)
        else:
            hist.Draw("hist same")
            hist.SetLineColor(goodColors[i])
            legend.AddEntry(hist,legendLabels[i],"l")
            #stack.Add(hist)
            
    legend.Draw()
    TriggerCanvas.Update()
    TriggerCanvas.Print(outputPDF + ".pdf","pdf")

    print legendLabels

    count = 0
    for i,hist in enumerate(histList):
        #if legendLabels[i] == 'allTriggers':
        #    continue
        individualTriggerCanvas = ROOT.TCanvas("cIndividualTriggers","2017 Leading pT")
        effHist = drawHistsWithEfficiencyPoints(hist, legendLabels[i], namesAndEffs, individualTriggerCanvas)
        if effHist == None:
            continue
        if effHist != None:
            count += 1
        hist.Draw("hist")
        effHist.Draw("hist same")
        individualTriggerCanvas.Update()
        if i == 1:
            #print "effHist main: ", effHist
            #hist.Draw("hist")
            #effHist.Draw("hist same")
            #individualTriggerCanvas.Update()
            #individualTriggerCanvas.Print(outputPDF + "_lineTest.pdf[","pdf")
            individualTriggerCanvas.Print(outputPDF + "_turnonTest.pdf[","pdf")
        else:
            #drawHistsWithEfficiencyPoints(hist, legendLabels[i], namesAndEffs, individualTriggerCanvas)
            #hist.Draw("hist")
            #effHist.Draw("hist same")
            #individualTriggerCanvas.Update()
            if i == (len(histList)-1):
                print "closing pdf"
                #individualTriggerCanvas.Print(outputPDF + "_lineTest.pdf]","pdf")
                individualTriggerCanvas.Print(outputPDF + "_turnonTest.pdf]","pdf")
            else:
                #individualTriggerCanvas.Print(outputPDF + "_lineTest.pdf","pdf")
                individualTriggerCanvas.Print(outputPDF + "_turnonTest.pdf","pdf")
    #individualTriggerCanvas.Print(outputPDF + "_lineTest.pdf]","pdf")
    individualTriggerCanvas.Print(outputPDF + "_turnonTest.pdf]","pdf")

    allTriggerCanvas = ROOT.TCanvas("cAllTrigger","2007 Leading pT")
    allTriggerHist = TFile1.Get("h_PtLeadingReference_allTriggers")
    allTriggerHist.SetTitle(plotTitle + "(All Triggers)")
    allTriggerHist.GetXaxis().SetTitle("pT(Lead) [GeV]")
    allTriggerHist.GetYaxis().SetTitle("Number of Events")
    allTriggerHist.SetStats(False)
    allTriggerHist.Draw("hist")
    allTriggerCanvas.Update()
    allTriggerCanvas.Print(outputPDF + "_allTrigger.pdf","pdf")
    
    histList.sort(reverse=False, key=getMax)
    for i,hist in enumerate(histList):
        hist.SetFillColor(hist.GetLineColor())
        stack.Add(hist)

    stackCanvas = ROOT.TCanvas("cStack","2017 Leading pT")
    stack.Draw("hist")
    stack.GetXaxis().SetTitle("p_{T,Lead} [GeV]")
    stack.GetYaxis().SetTitle("Number of Recorded Events")
    #stack.Draw("hist")
    legend.Draw()
    stackCanvas.Update()
    stackCanvas.Print(outputPDF + "_THStack.pdf","pdf")

    print legendLabels
    #print histList
    #print histMaximums
        

    #hPtLead_j15_2017 = TFile1.Get("h_PtLeadingReference_HLT_j15")
    #hPtLead_j25_2017 = TFile1.Get("h_PtLeadingReference_HLT_j25")
    #hPtLead_j35_2017 = TFile1.Get("h_PtLeadingReference_HLT_j35")
    #hPtLead_j45_2017 = TFile1.Get("h_PtLeadingReference_HLT_j45")
    #hPtLead_j60_2017 = TFile1.Get("h_PtLeadingReference_HLT_j60")
    #hPtLead_j85_2017 = TFile1.Get("h_PtLeadingReference_HLT_j85")
    #hPtLead_j110_2017 = TFile1.Get("h_PtLeadingReference_HLT_j110")
    #hPtLead_j150_2017 = TFile1.Get("h_PtLeadingReference_HLT_j150")
    #hPtLead_j175_2017 = TFile1.Get("h_PtLeadingReference_HLT_j175")
    #hPtLead_j260_2017 = TFile1.Get("h_PtLeadingReference_HLT_j260")
    #hPtLead_j320_2017 = TFile1.Get("h_PtLeadingReference_HLT_j320")
    #hPtLead_j340_2017 = TFile1.Get("h_PtLeadingReference_HLT_j340")
    #hPtLead_j360_2017 = TFile1.Get("h_PtLeadingReference_HLT_j360")
    #hPtLead_j380_2017 = TFile1.Get("h_PtLeadingReference_HLT_j380")
    #hPtLead_j400_2017 = TFile1.Get("h_PtLeadingReference_HLT_j400")
    #hPtLead_j420_2017 = TFile1.Get("h_PtLeadingReference_HLT_j420")

    #TriggerCanvas2017 = ROOT.TCanvas("c2017Triggers","2017 Leading pT")
    #legend2017 = ROOT.TLegend(0.576493,0.739812,0.776119,0.899687)
    #hPtLead_j15_2017.SetTitle("2017 Data")
    #hPtLead_j15_2017.GetXaxis().SetTitle("pT(leading) [GeV]")
    #hPtLead_j15_2017.Draw("hist")
    #hPtLead_j420_2017.SetLineColor(1)
    #hPtLead_j380_2017.SetLineColor(2)
    #hPtLead_j360_2017.SetLineColor(3)
    #hPtLead_j340_2017.SetLineColor(4)
    #hPtLead_j320_2017.SetLineColor(5)
    #hPtLead_j260_2017.SetLineColor(6)
    #hPtLead_j175_2017.SetLineColor(7)
    #hPtLead_j150_2017.SetLineColor(8)
    #hPtLead_j110_2017.SetLineColor(9)
    #hPtLead_j85_2017.SetLineColor(10)
    #hPtLead_j60_2017.SetLineColor(11)
    #hPtLead_j45_2017.SetLineColor(12)
    #hPtLead_j35_2017.SetLineColor(13)
    #hPtLead_j25_2017.SetLineColor(14)
    #hPtLead_j420_2017.Draw("hist sames")
    #hPtLead_j380_2017.Draw("hist sames")
    #hPtLead_j360_2017.Draw("hist sames")
    #hPtLead_j340_2017.Draw("hist sames")
    #hPtLead_j320_2017.Draw("hist sames")
    #hPtLead_j260_2017.Draw("hist sames")
    #hPtLead_j175_2017.Draw("hist sames")
    #hPtLead_j150_2017.Draw("hist sames")
    #hPtLead_j110_2017.Draw("hist sames")
    #hPtLead_j85_2017.Draw("hist sames")
    #hPtLead_j60_2017.Draw("hist sames")
    #hPtLead_j45_2017.Draw("hist sames")
    #hPtLead_j35_2017.Draw("hist sames")
    #hPtLead_j25_2017.Draw("hist sames")
    #ROOT.gPad.Update()
    #statbox_j380 = hPtLead_j380_2017.FindObject("stats")
    #statbox_j380.SetX1NDC(0.77927)
    #statbox_j380.SetX2NDC(0.979943)
    #statbox_j380.SetY1NDC(0.613108)
    #statbox_j380.SetY2NDC(0.773784)
    #statbox_j360 = hPtLead_j360_2017.FindObject("stats")
    #statbox_j360.SetX1NDC(0.77927)
    #statbox_j360.SetX2NDC(0.979943)
    #statbox_j360.SetY1NDC(0.457680)
    #statbox_j360.SetY2NDC(0.617555)
    #legend2017.AddEntry(hPtLead_j420_2017, "j420", "l")
    #legend2017.AddEntry(hPtLead_j380_2017, "j380", "l")
    #legend2017.AddEntry(hPtLead_j360_2017, "j360", "l")
    #legend2017.AddEntry(hPtLead_j340_2017, "j340", "l")
    #legend2017.AddEntry(hPtLead_j320_2017, "j320", "l")
    #legend2017.AddEntry(hPtLead_j260_2017, "j260", "l")
    #legend2017.AddEntry(hPtLead_j175_2017, "j175", "l")
    #legend2017.AddEntry(hPtLead_j150_2017, "j150", "l")
    #legend2017.AddEntry(hPtLead_j110_2017, "j110", "l")
    #legend2017.AddEntry(hPtLead_j85_2017, "j85", "l")
    #legend2017.AddEntry(hPtLead_j60_2017, "j60", "l")
    #legend2017.AddEntry(hPtLead_j45_2017, "j45", "l")
    #legend2017.AddEntry(hPtLead_j35_2017, "j35", "l")
    #legend2017.AddEntry(hPtLead_j25_2017, "j25", "l")
    #legend2017.AddEntry(hPtLead_j15_2017, "j15", "l")
    #legend2017.Draw()
    #TriggerCanvas2017.Update()
    #TriggerCanvas2017.Print("TriggerImprovements_2017_allHLT.pdf","pdf")

def getMax(histogram):
    return histogram.GetMaximum()
    
def drawHistsWithEfficiencyPoints(hist, label, namesEffDict, canvas):
    if label not in namesEffDict.keys():
        print label, " does not exist in dictionaries"
        return None
    for key in namesEffDict.keys():
        if key == label:
            print "key == label success"
            effPoint95 = namesEffDict[key]['0.95']
            #print effPoint95
            effPoint99 = namesEffDict[key]['0.99']
            effPoint995 = namesEffDict[key]['0.995']
            hist.Draw("hist")
            canvas.Update()
            effHist95 = hist.Clone()
            effHist99 = hist.Clone()
            effHist995 = hist.Clone()
            #print "effHist: ", effHist
            for bin in range(hist.GetNbinsX()):
                if bin >= 1 and bin < effPoint95:
                    effHist95.SetBinContent(bin, 0.0)
                if bin >= 1 and bin < effPoint99:
                    effHist99.SetBinContent(bin, 0.0)
                if bin >= 1 and bin < effPoint995:
                    effHist995.SetBinContent(bin, 0.0)
            #ymax = hist.GetMaximum()
            #ymax = ROOT.gPad.GetUymax()
            #print "ymax: ", ymax
            #line95 = ROOT.TLine(effPoint95,0,effPoint95,ymax)
            #line95.SetLineColor(2)
            #line95.SetLineStyle(9)
            #line95.Draw()
            effHist95.SetLineStyle(2)
            effHist95.Draw("hist")
            effHist99.SetLineStyle(2)
            effHist99.Draw("hist")
            effHist995.SetLineStyle(2)
            effHist995.Draw("hist")
            canvas.Update()
            return effHist995
            #return effHist99
            #return effHist95
        
    
main()
