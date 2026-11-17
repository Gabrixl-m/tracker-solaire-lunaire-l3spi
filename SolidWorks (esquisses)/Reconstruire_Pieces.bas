' ==============================================================================================
'  Reconstruire_Pieces  -  macro SolidWorks (VBA)
'
'  Refait dans SolidWorks, avec de vraies esquisses et de vraies fonctions (extrusions,
'  enlevements de matiere, revolutions, balayage helicoidal), les pieces imprimees du cas
'  terrestre. Elle lit les fichiers du dossier "donnees" (un par piece), ecrits par
'  scripts/generate_esquisses_solidworks.py, et enregistre un .SLDPRT par piece dans "pieces".
'
'  Apres chaque fonction, la macro mesure le volume et le centre de gravite de la piece et les
'  compare aux valeurs attendues : si le sens d'une extrusion est mauvais, elle la supprime et
'  essaie l'autre. Tout est note dans "pieces\journal.txt".
'
'  Mode d'emploi : voir README.md du meme dossier.
'  (Pas d'accents dans ce fichier : l'editeur VBA ne lit pas l'UTF-8.)
' ==============================================================================================
Option Explicit

Const MM As Double = 0.001                 ' les fichiers sont en mm, l'API en metres
Const PI As Double = 3.14159265358979

Dim swApp As Object
Dim swModel As Object
Dim swMath As Object
Dim swSkMgr As Object
Dim swFeatMgr As Object

Dim gPlan(1 To 3) As Object                ' les trois plans de base de la piece
Dim gSk As Object                          ' esquisse ouverte
Dim gXf As Object                          ' transformation modele -> esquisse
Dim gJournal As Integer

Dim gVa As Double, gMa(2) As Double        ' etat mesure apres la derniere fonction reussie (mm3, mm4)
Dim gVe As Double, gMe(2) As Double        ' etat attendu au meme moment
Dim gVmes As Double                        ' dernier volume mesure (pour le journal)

Dim gSens(1) As Integer                    ' sens appris des extrusions (0 = ajout, 1 = enlevement)
Dim gFlip As Object                        ' sens appris du decalage de depart
Dim gHelice As Long                        ' reglage d'helice qui a marche (-1 : aucun)

Dim gNbFonctions As Long, gNbEchecs As Long
Dim gTraces As Long, gRefus As Long        ' entites tracees / refusees par SolidWorks dans la derniere esquisse
Dim gDerDV As Double                       ' derniere variation de volume mesuree (mm3)
Dim gDerErr As String                      ' derniere erreur VBA rencontree par Extruder
Dim gAlerte As String                      ' observation sur la derniere esquisse (pour le journal)
Dim gXinfo As String                       ' transformation modele -> esquisse de la derniere esquisse
Dim gR(8) As Double, gT(2) As Double, gS As Double   ' matrice, translation et echelle de cette transformation
Dim gRow As Boolean                        ' convention de la matrice (False : colonnes, True : lignes)
Dim gCalibre As Boolean                    ' la convention a-t-elle ete calibree ?

' ----------------------------------------------------------------------------------------------
Sub main()
    Dim dDon As String, dSortie As String, f As String
    Dim noms() As String, n As Long, i As Long
    Dim nbOk As Long, nbKo As Long, bilan As String

    Set swApp = Application.SldWorks
    Set swMath = swApp.GetMathUtility
    Set gFlip = CreateObject("Scripting.Dictionary")
    gHelice = -1
    gSens(0) = 0: gSens(1) = 0

    If Not TrouverDossiers(dDon, dSortie) Then
        MsgBox "Dossier ""donnees"" introuvable : rien n'a ete fait.", vbExclamation
        Exit Sub
    End If
    If Dir(dSortie, vbDirectory) = "" Then MkDir dSortie

    f = Dir(dDon & "*.txt")
    Do While f <> ""
        ReDim Preserve noms(n)
        noms(n) = f
        n = n + 1
        f = Dir
    Loop
    If n = 0 Then
        MsgBox "Aucun fichier .txt dans " & dDon, vbExclamation
        Exit Sub
    End If

    gJournal = FreeFile
    Open dSortie & "journal.txt" For Output As #gJournal
    Print #gJournal, "Reconstruction des pieces - " & Now
    Print #gJournal, "SolidWorks " & swApp.RevisionNumber
    Print #gJournal, ""

    For i = 0 To n - 1
        If TraiterPiece(dDon & noms(i), dSortie) Then
            nbOk = nbOk + 1
        Else
            nbKo = nbKo + 1
            bilan = bilan & vbCrLf & "   - " & Left$(noms(i), Len(noms(i)) - 4)
            If nbOk = 0 And nbKo >= 2 Then
                Print #gJournal, ""
                Print #gJournal, "ARRET : les deux premieres pieces ont echoue, inutile de continuer (voir les lignes ci-dessus)."
                bilan = bilan & vbCrLf & "   (arret apres deux echecs de suite)"
                Exit For
            End If
        End If
    Next i

    Print #gJournal, ""
    Print #gJournal, "BILAN : " & nbOk & " piece(s) conforme(s), " & nbKo & " a reprendre."
    Close #gJournal

    If nbKo = 0 Then
        MsgBox nbOk & " pieces refaites et conformes." & vbCrLf & "Fichiers : " & dSortie, vbInformation
    Else
        MsgBox nbOk & " piece(s) conforme(s), " & nbKo & " a reprendre :" & bilan & vbCrLf & vbCrLf & _
               "Detail dans " & dSortie & "journal.txt", vbExclamation
    End If
End Sub

' Dossier des donnees (a cote de la macro, sinon demande) et dossier de sortie
Function TrouverDossiers(ByRef dDon As String, ByRef dSortie As String) As Boolean
    Dim p As String, k As Long, sh As Object, fo As Object
    TrouverDossiers = False
    On Error Resume Next
    p = swApp.GetCurrentMacroPathName
    On Error GoTo 0
    k = InStrRev(p, "\")
    If k > 0 Then
        p = Left$(p, k)
        If Dir(p & "donnees\*.txt") <> "" Then
            dDon = p & "donnees\"
            dSortie = p & "pieces\"
            TrouverDossiers = True
            Exit Function
        End If
    End If
    On Error Resume Next
    Set sh = CreateObject("Shell.Application")
    Set fo = sh.BrowseForFolder(0, "Choisir le dossier ""SolidWorks (esquisses)"" (celui qui contient ""donnees"")", 0)
    If fo Is Nothing Then Exit Function
    p = fo.Self.Path
    On Error GoTo 0
    If p = "" Then Exit Function
    If Right$(p, 1) <> "\" Then p = p & "\"
    If Dir(p & "donnees\*.txt") <> "" Then
        dDon = p & "donnees\"
        dSortie = p & "pieces\"
        TrouverDossiers = True
    ElseIf Dir(p & "*.txt") <> "" Then
        dDon = p
        dSortie = p & "pieces\"
        TrouverDossiers = True
    End If
End Function

' ----------------------------------------------------------------------------------------------
'  Une piece
' ----------------------------------------------------------------------------------------------
Function TraiterPiece(fichier As String, dSortie As String) As Boolean
    Dim fn As Integer, s As String, lignes() As String
    Dim nom As String, i As Long, j As Long, numero As Long, k As Long
    Dim chemin As String, r As Long, echecs As Long

    TraiterPiece = False
    fn = FreeFile
    Open fichier For Input As #fn
    s = Input$(LOF(fn), fn)
    Close #fn
    lignes = Split(Replace(s, vbCr, ""), vbLf)
    If UBound(lignes) < 2 Then Exit Function
    nom = Trim$(Mid$(lignes(0), 7))

    Print #gJournal, "=== " & nom
    Set swModel = NouvellePiece()
    If swModel Is Nothing Then
        Print #gJournal, "  ECHEC : impossible de creer une piece (gabarit de piece par defaut ?)"
        Exit Function
    End If
    Set swSkMgr = swModel.SketchManager
    Set swFeatMgr = swModel.FeatureManager
    TrouverPlans
    If gPlan(3) Is Nothing Then
        Print #gJournal, "  ECHEC : plans de base introuvables"
        Exit Function
    End If
    Calibrer
    swSkMgr.AddToDB = False
    swSkMgr.DisplayWhenAdded = True

    gVa = 0: gVe = 0
    For k = 0 To 2
        gMa(k) = 0: gMe(k) = 0
    Next k
    gNbFonctions = 0: gNbEchecs = 0

    i = 1
    Do While i <= UBound(lignes)
        If Left$(lignes(i), 2) = "F " Then
            j = i + 1
            Do While j <= UBound(lignes)
                If Left$(lignes(j), 2) = "F " Or Left$(lignes(j), 3) = "FIN" Then Exit Do
                j = j + 1
            Loop
            numero = numero + 1
            gNbFonctions = gNbFonctions + 1
            On Error Resume Next
            Err.Clear
            FaireFonction lignes, i, j - 1, numero
            If Err.Number <> 0 Then
                Print #gJournal, "  " & Format$(numero, "00") & " ERREUR VBA : " & Err.Description
                gNbEchecs = gNbEchecs + 1
                Err.Clear
                If Not swSkMgr.ActiveSketch Is Nothing Then swSkMgr.InsertSketch True
            End If
            On Error GoTo 0
            If gNbEchecs > 0 Then
                Print #gJournal, "  (les fonctions suivantes ne sont pas essayees : la piece reste ouverte pour examen)"
                Exit Do
            End If
            i = j
        Else
            i = i + 1
        End If
    Loop

    swSkMgr.AddToDB = False
    swSkMgr.DisplayWhenAdded = True
    echecs = gNbEchecs
    On Error Resume Next
    swModel.ClearSelection2 True
    swModel.ForceRebuild3 False
    swModel.ShowNamedView2 "*Isometric", 7
    swModel.ViewZoomtofit2
    If echecs = 0 Then
        chemin = dSortie & nom & ".SLDPRT"
    Else
        chemin = dSortie & nom & "_A_REPRENDRE.SLDPRT"
    End If
    If Dir(chemin) <> "" Then Kill chemin
    Err.Clear
    r = swModel.SaveAs3(chemin, 0, 1)
    If Err.Number <> 0 Or r <> 0 Then
        Print #gJournal, "  enregistrement : code " & r & " " & Err.Description & " (enregistrer la piece a la main)"
    End If
    Err.Clear
    On Error GoTo 0

    Print #gJournal, "  -> " & gNbFonctions & " fonctions, " & echecs & " echec(s) ; volume final " & _
                     Format$(gVmes, "0.00") & " mm3, attendu " & Format$(gVe, "0.00")
    If echecs = 0 Then
        TraiterPiece = True
        On Error Resume Next
        swApp.CloseDoc swModel.GetTitle       ' les pieces a reprendre restent ouvertes
        On Error GoTo 0
    End If
End Function

Function NouvellePiece() As Object
    Dim m As Object, gabarit As String
    On Error Resume Next
    Set m = swApp.NewPart
    If m Is Nothing Then
        gabarit = swApp.GetUserPreferenceStringValue(8)      ' gabarit de piece par defaut
        Set m = swApp.NewDocument(gabarit, 0, 0#, 0#)
    End If
    On Error GoTo 0
    Set NouvellePiece = m
End Function

' Les trois premiers plans de l'arbre : face, dessus, droite (quel que soit leur nom)
Sub TrouverPlans()
    Dim f As Object, k As Long
    For k = 1 To 3
        Set gPlan(k) = Nothing
    Next k
    k = 0
    Set f = swModel.FirstFeature
    Do While Not f Is Nothing
        If f.GetTypeName2 = "RefPlane" Then
            k = k + 1
            Set gPlan(k) = f
            If k = 3 Then Exit Do
        End If
        Set f = f.GetNextFeature
    Loop
End Sub

' ----------------------------------------------------------------------------------------------
'  Une fonction : lignes(i0) = "F ...", lignes(i0+1) = "P ...", puis les contours jusqu'a i1
' ----------------------------------------------------------------------------------------------
Sub FaireFonction(lignes() As String, i0 As Long, i1 As Long, numero As Long)
    Dim t() As String, p() As String
    Dim o(2) As Double, n(2) As Double
    Dim estCut As Boolean, k As Long

    t = Split(lignes(i0), " ")
    p = Split(lignes(i0 + 1), " ")
    For k = 0 To 2
        o(k) = Val(p(1 + k))
        n(k) = Val(p(4 + k))
    Next k
    estCut = (t(1) = "CUT")

    Select Case t(2)
        Case "EXT"
            FaireExtrusion lignes, i0, i1, numero, t, o, n, estCut
        Case "REV"
            FaireRevolution lignes, i0, i1, numero, t, o, n, estCut
        Case "HEL"
            FaireHelice lignes, i0, i1, numero, t, o, n
        Case Else
            Print #gJournal, "  " & Format$(numero, "00") & " type inconnu : " & t(2)
            gNbEchecs = gNbEchecs + 1
    End Select
End Sub

' Etat attendu apres la fonction : t(iv) = volume, t(iv+1..iv+3) = centre de gravite, puis tolerances
Sub LireEtat(t() As String, iv As Long, ByRef Ve As Double, Ge() As Double, ByRef tolV As Double, ByRef tolG As Double)
    Ve = Val(t(iv))
    Ge(0) = Val(t(iv + 1)): Ge(1) = Val(t(iv + 2)): Ge(2) = Val(t(iv + 3))
    tolV = Val(t(iv + 4))
    tolG = Val(t(iv + 5))
End Sub

Sub AvancerAttendu(Ve As Double, Ge() As Double)
    Dim k As Long
    gVe = Ve
    For k = 0 To 2
        gMe(k) = Ve * Ge(k)
    Next k
End Sub

' --- extrusion (ajout ou enlevement) de a0 a a1 le long de d, esquisse dans le plan passant par l'origine
Sub FaireExtrusion(lignes() As String, i0 As Long, i1 As Long, numero As Long, t() As String, _
                   o() As Double, n() As Double, estCut As Boolean)
    Dim a0 As Double, a1 As Double
    Dim Ve As Double, Ge(2) As Double, tolV As Double, tolG As Double
    Dim nomSk As String, nomF As String, idx As Long, passe As Long, ok As Boolean
    Dim detail As String

    a0 = Val(t(6)): a1 = Val(t(7))
    LireEtat t, 8, Ve, Ge, tolV, tolG
    nomSk = "Esquisse_" & Format$(numero, "00")
    If estCut Then
        nomF = "Enlevement_" & Format$(numero, "00")
        idx = 1
    Else
        nomF = "Extrusion_" & Format$(numero, "00")
        idx = 0
    End If

    ' passe 0 : trace normal ; passe 1 : trace "direct dans la base" (AddToDB), si la passe 0 echoue
    For passe = 0 To 1
        swSkMgr.AddToDB = (passe = 1)
        ok = EssaiExtrusion(lignes, i0, i1, numero, o, n, a0, a1, Ve, Ge, tolV, tolG, nomSk, nomF, estCut, idx, passe, detail)
        swSkMgr.AddToDB = False
        If ok Then Exit For
        Print #gJournal, "     " & detail
        If passe = 0 Then Supprimer swModel.FeatureByName(nomSk)
    Next passe

    If Not ok Then
        Print #gJournal, "  " & Format$(numero, "00") & " " & nomF & " : ECHEC ; l'esquisse """ & nomSk & _
                         "_A_REPRENDRE"" est restee dans l'arbre (de " & Format$(a0, "0.000") & " a " & _
                         Format$(a1, "0.000") & " mm le long de " & t(3) & " " & t(4) & " " & t(5) & ")"
        Renommer nomSk, nomSk & "_A_REPRENDRE"
        gNbEchecs = gNbEchecs + 1
    End If
    AvancerAttendu Ve, Ge
End Sub

Function EssaiExtrusion(lignes() As String, i0 As Long, i1 As Long, numero As Long, o() As Double, n() As Double, _
                        a0 As Double, a1 As Double, Ve As Double, Ge() As Double, tolV As Double, tolG As Double, _
                        nomSk As String, nomF As String, estCut As Boolean, idx As Long, passe As Long, _
                        ByRef detail As String) As Boolean
    Dim b0 As Double, b1 As Double, q0 As Variant, q1 As Variant, s As Double
    Dim sk As Object, f As Object
    Dim score As Long, q As Long, sens As Boolean, e As Integer, flip As Boolean
    Dim c As Double, cle As String, sA As Long, sB As Long
    Dim verifiable As Boolean, essais As Long, crees As Long, fait As Boolean
    Dim traces As Long, refus As Long, mesure As String

    EssaiExtrusion = False
    detail = "passe " & (passe + 1) & " (" & IIf(passe = 0, "trace normal", "trace direct") & ") : "
    If Not OuvrirEsquisse(o, n, numero) Then
        detail = detail & "plan d'esquisse impossible a creer"
        Exit Function
    End If
    ' sens de la normale de l'esquisse par rapport a la direction d'extrusion
    q0 = VersEsquisse(o(0), o(1), o(2))
    q1 = VersEsquisse(o(0) + n(0), o(1) + n(1), o(2) + n(2))
    s = q1(2) - q0(2)
    If s > 0 Then
        b0 = a0: b1 = a1
    Else
        b0 = -a1: b1 = -a0
    End If
    Dessiner lignes, i0 + 2, i1
    traces = gTraces: refus = gRefus
    Set sk = FermerEsquisse(nomSk)
    If sk Is Nothing Then
        detail = detail & "esquisse vide apres trace (" & traces & " entites tracees, " & refus & " refusees)"
        Exit Function
    End If

    ' 8 reglages possibles (sens, hypothese sur le sens reel, inversion du decalage) : ceux qui
    ' ont deja marche sont essayes d'abord ; le controle volume + centre de gravite tranche
    For score = 8 To 0 Step -1
        For q = 0 To 7
            sens = ((q And 1) <> 0)
            If (q And 2) <> 0 Then e = -1 Else e = 1
            flip = ((q And 4) <> 0)
            If e > 0 Then c = b0 Else c = b1
            cle = idx & "/" & e & "/" & Sgn(c)
            If gSens(idx) = 0 Then
                sA = 1
            ElseIf (sens And e = -gSens(idx)) Or ((Not sens) And e = gSens(idx)) Then
                sA = 2
            Else
                sA = 0
            End If
            If Abs(c) < 0.000001 Then
                If flip Then sB = -99 Else sB = 2
            ElseIf Not gFlip.Exists(cle) Then
                sB = 1
            ElseIf gFlip(cle) = flip Then
                sB = 2
            Else
                sB = 0
            End If
            If sA * 3 + sB = score Then
                essais = essais + 1
                Set f = Extruder(nomSk, estCut, b0, b1, sens, e, flip)
                If Not f Is Nothing Then
                    crees = crees + 1
                    If Conforme(Ve, Ge, tolV, tolG, verifiable) Then
                        f.Name = nomF
                        If verifiable Then
                            If sens Then gSens(idx) = -e Else gSens(idx) = e
                            If Abs(c) >= 0.000001 Then gFlip(cle) = flip
                        End If
                        fait = True
                    Else
                        mesure = "variation de volume mesuree " & Format$(gDerDV, "0.000") & " mm3"
                        Supprimer f
                    End If
                End If
            End If
            If fait Then Exit For
        Next q
        If fait Then Exit For
    Next score

    If fait Then
        Print #gJournal, "  " & Format$(numero, "00") & " " & nomF & " : OK (" & essais & " essai(s), " & _
                         IIf(passe = 0, "trace normal", "trace direct") & ") V = " & _
                         Format$(gVmes, "0.000") & " / " & Format$(Ve, "0.000") & IIf(verifiable, "", "  [petite fonction : sens non controle]")
        EssaiExtrusion = True
    Else
        detail = detail & traces & " entites tracees, " & refus & " refusees ; " & essais & " essais, " & crees & _
                 " extrusion(s) creee(s)" & IIf(mesure <> "", " ; " & mesure & ", attendu " & Format$(Ve - gVe, "0.000") & " mm3", "") & _
                 IIf(gDerErr <> "", " ; derniere erreur VBA : " & gDerErr, "") & vbCrLf & "        " & gAlerte & vbCrLf & _
                 "        transformation modele->esquisse : " & gXinfo
    End If
End Function

Function Extruder(nomSk As String, estCut As Boolean, b0 As Double, b1 As Double, _
                  sens As Boolean, e As Integer, flip As Boolean) As Object
    Dim c As Double, t0 As Long, prof As Double, f As Object, sk As Object
    prof = (b1 - b0) * MM
    If e > 0 Then c = b0 Else c = b1
    If Abs(c) < 0.000001 Then t0 = 0 Else t0 = 3          ' 0 = plan d'esquisse, 3 = decalage
    Set Extruder = Nothing
    Set sk = swModel.FeatureByName(nomSk)
    If sk Is Nothing Then Exit Function
    gDerErr = ""
    swModel.ClearSelection2 True
    If Not sk.Select2(False, 0) Then
        swModel.Extension.SelectByID2 nomSk, "SKETCH", 0#, 0#, 0#, False, 0, Nothing, 0
    End If
    On Error Resume Next
    If estCut Then
        Set f = swFeatMgr.FeatureCut4(True, False, sens, 0, 0, prof, 0#, False, False, False, False, 0#, 0#, _
                                      False, False, False, False, False, True, True, True, True, False, _
                                      t0, Abs(c) * MM, flip, False)
        If f Is Nothing Then
            Err.Clear
            Set f = swFeatMgr.FeatureCut3(True, False, sens, 0, 0, prof, 0#, False, False, False, False, 0#, 0#, _
                                          False, False, False, False, False, True, True, True, True, False, _
                                          t0, Abs(c) * MM, flip)
        End If
    Else
        Set f = swFeatMgr.FeatureExtrusion3(True, False, sens, 0, 0, prof, 0#, False, False, False, False, 0#, 0#, _
                                            False, False, False, False, True, True, True, t0, Abs(c) * MM, flip)
        If f Is Nothing Then
            Err.Clear
            Set f = swFeatMgr.FeatureExtrusion2(True, False, sens, 0, 0, prof, 0#, False, False, False, False, 0#, 0#, _
                                                False, False, False, False, True, True, True, t0, Abs(c) * MM, flip)
        End If
    End If
    If Err.Number <> 0 Then gDerErr = Err.Number & " " & Err.Description
    Err.Clear
    On Error GoTo 0
    swModel.ClearSelection2 True
    Set Extruder = f
End Function

' --- revolution complete (ajout ou enlevement) autour de l'axe (p, d), profil dans un plan contenant l'axe
Sub FaireRevolution(lignes() As String, i0 As Long, i1 As Long, numero As Long, t() As String, _
                    o() As Double, n() As Double, estCut As Boolean)
    Dim px As Double, py As Double, pz As Double, dx As Double, dy As Double, dz As Double
    Dim Ve As Double, Ge(2) As Double, tolV As Double, tolG As Double
    Dim a As Variant, b As Variant, axe As Object, sk As Object, f As Object, sd As Object
    Dim nomSk As String, nomF As String, essai As Long, verifiable As Boolean, fait As Boolean

    px = Val(t(3)): py = Val(t(4)): pz = Val(t(5))
    dx = Val(t(6)): dy = Val(t(7)): dz = Val(t(8))
    LireEtat t, 9, Ve, Ge, tolV, tolG
    nomSk = "Esquisse_" & Format$(numero, "00")
    If estCut Then nomF = "Enlevement_revolution_" & Format$(numero, "00") Else nomF = "Revolution_" & Format$(numero, "00")

    If Not OuvrirEsquisse(o, n, numero) Then
        Print #gJournal, "  " & Format$(numero, "00") & " " & nomF & " : ECHEC, plan d'esquisse impossible a creer"
        gNbEchecs = gNbEchecs + 1
        AvancerAttendu Ve, Ge
        Exit Sub
    End If
    Dessiner lignes, i0 + 2, i1
    a = VersEsquisse(px - 80 * dx, py - 80 * dy, pz - 80 * dz)
    b = VersEsquisse(px + 80 * dx, py + 80 * dy, pz + 80 * dz)
    Set axe = swSkMgr.CreateCenterLine(a(0), a(1), 0#, b(0), b(1), 0#)
    Set sk = FermerEsquisse(nomSk)

    fait = False
    For essai = 0 To 1
        Set sk = swModel.FeatureByName(nomSk)
        swModel.ClearSelection2 True
        sk.Select2 False, 0
        On Error Resume Next
        If essai = 0 Then                          ' axe de revolution : la ligne de construction (marque 16)
            Set sd = swModel.SelectionManager.CreateSelectData
            sd.Mark = 16
            axe.Select4 True, sd
        End If
        Set f = Nothing
        Set f = swFeatMgr.FeatureRevolve2(True, True, False, estCut, False, False, 0, 0, 2 * PI, 0#, _
                                          False, False, 0#, 0#, 0, 0#, 0#, True, True, True)
        Err.Clear
        On Error GoTo 0
        swModel.ClearSelection2 True
        If Not f Is Nothing Then
            If Conforme(Ve, Ge, tolV, tolG, verifiable) Then
                f.Name = nomF
                fait = True
                Exit For
            Else
                Supprimer f
            End If
        End If
    Next essai

    If fait Then
        Print #gJournal, "  " & Format$(numero, "00") & " " & nomF & " : OK V = " & Format$(gVmes, "0.000") & " / " & Format$(Ve, "0.000")
    Else
        Print #gJournal, "  " & Format$(numero, "00") & " " & nomF & " : ECHEC ; l'esquisse """ & nomSk & _
                         "_A_REPRENDRE"" est restee dans l'arbre (revolution de 360 deg autour de sa ligne de construction)"
        Renommer nomSk, nomSk & "_A_REPRENDRE"
        gNbEchecs = gNbEchecs + 1
    End If
    AvancerAttendu Ve, Ge
End Sub

' --- filet : profil balaye le long d'une helice d'axe Z qui part du point (rayon, 0, 0) et monte a droite
Sub FaireHelice(lignes() As String, i0 As Long, i1 As Long, numero As Long, t() As String, _
                o() As Double, n() As Double)
    Dim rayon As Double, pas As Double, haut As Double
    Dim Ve As Double, Ge(2) As Double, tolV As Double, tolG As Double
    Dim oz(2) As Double, nz(2) As Double
    Dim nomC As String, nomP As String, nomH As String, nomF As String
    Dim angles(6) As Double, ordre(28) As Long, nb As Long, k As Long, q As Long
    Dim ia As Long, horaire As Boolean, inverse As Boolean
    Dim hel As Object, prof As Object, cercle As Object, f As Object
    Dim verifiable As Boolean, fait As Boolean, essais As Long, avant As Long

    rayon = Val(t(3)): pas = Val(t(4)): haut = Val(t(5))
    LireEtat t, 6, Ve, Ge, tolV, tolG
    nomC = "Esquisse_cercle_helice_" & Format$(numero, "00")
    nomP = "Esquisse_profil_filet_" & Format$(numero, "00")
    nomH = "Helice_" & Format$(numero, "00")
    nomF = "Filet_" & Format$(numero, "00")

    ' cercle de base de l'helice, dans le plan Z = 0
    oz(0) = 0: oz(1) = 0: oz(2) = 0
    nz(0) = 0: nz(1) = 0: nz(2) = 1
    If Not OuvrirEsquisse(oz, nz, numero) Then
        Print #gJournal, "  " & Format$(numero, "00") & " " & nomF & " : ECHEC, plan du cercle"
        gNbEchecs = gNbEchecs + 1
        AvancerAttendu Ve, Ge
        Exit Sub
    End If
    swSkMgr.CreateCircleByRadius 0#, 0#, 0#, rayon * MM
    Set cercle = FermerEsquisse(nomC)
    ' profil du filet, dans le plan qui contient l'axe et le depart de l'helice
    If Not OuvrirEsquisse(o, n, numero) Then
        Print #gJournal, "  " & Format$(numero, "00") & " " & nomF & " : ECHEC, plan du profil"
        gNbEchecs = gNbEchecs + 1
        AvancerAttendu Ve, Ge
        Exit Sub
    End If
    Dessiner lignes, i0 + 2, i1
    Set prof = FermerEsquisse(nomP)

    ' sens de rotation, sens de montee et angle de depart : la convention de l'API n'est pas
    ' supposee, tous les reglages sont essayes et le controle (volume + centre de gravite) tranche
    angles(0) = 0: angles(1) = PI / 2: angles(2) = PI: angles(3) = 3 * PI / 2
    angles(4) = 90: angles(5) = 180: angles(6) = 270
    nb = 0
    If gHelice >= 0 Then
        ordre(0) = gHelice
        nb = 1
    End If
    For q = 0 To 27
        If q <> gHelice Then
            ordre(nb) = q
            nb = nb + 1
        End If
    Next q

    fait = False
    For k = 0 To nb - 1
        q = ordre(k)
        ia = q \ 4
        horaire = ((q And 1) <> 0)
        inverse = ((q And 2) <> 0)
        essais = essais + 1
        Set cercle = swModel.FeatureByName(nomC)
        Set hel = Nothing
        Set f = Nothing
        avant = swModel.GetFeatureCount
        swModel.ClearSelection2 True
        cercle.Select2 False, 0
        On Error Resume Next
        swModel.InsertHelix inverse, horaire, False, False, 2, haut * MM, pas * MM, haut / pas, 0#, angles(ia)
        Err.Clear
        On Error GoTo 0
        If swModel.GetFeatureCount > avant Then Set hel = swModel.FeatureByPositionReverse(0)
        If Not hel Is Nothing Then
            If hel.GetTypeName2 <> "Helix" Then Set hel = Nothing
        End If
        If Not hel Is Nothing Then
            Set prof = swModel.FeatureByName(nomP)
            swModel.ClearSelection2 True
            prof.Select2 False, 1                  ' profil : marque 1
            hel.Select2 True, 4                    ' trajectoire : marque 4
            On Error Resume Next
            Set f = swFeatMgr.InsertProtrusionSwept4(False, False, 0, False, False, 0, 0, False, 0#, 0#, 0, 0, _
                                                     True, True, True, 0#, True, False, 0#, 0)
            If f Is Nothing Then
                Err.Clear
                Set f = swFeatMgr.InsertProtrusionSwept3(False, False, 0, False, False, 0, 0, False, 0#, 0#, 0, 0, _
                                                         True, True, True, 0#, True)
            End If
            Err.Clear
            On Error GoTo 0
            swModel.ClearSelection2 True
            If Not f Is Nothing Then
                If Conforme(Ve, Ge, tolV, tolG, verifiable) Then
                    f.Name = nomF
                    hel.Name = nomH
                    gHelice = q
                    fait = True
                    Exit For
                End If
                Supprimer f
            End If
            Supprimer hel
        End If
    Next k

    If fait Then
        Print #gJournal, "  " & Format$(numero, "00") & " " & nomF & " : OK (" & essais & " essai(s)) V = " & _
                         Format$(gVmes, "0.000") & " / " & Format$(Ve, "0.000")
    Else
        Print #gJournal, "  " & Format$(numero, "00") & " " & nomF & " : ECHEC apres " & essais & " essais ; restent dans l'arbre le cercle """ & _
                         nomC & """ et le profil """ & nomP & """ (helice a droite, pas " & Format$(pas, "0.0000") & _
                         " mm, hauteur " & Format$(haut, "0.00") & " mm, depart sur l'axe X, puis balayage du profil)"
        gNbEchecs = gNbEchecs + 1
    End If
    AvancerAttendu Ve, Ge
End Sub

' ----------------------------------------------------------------------------------------------
'  Esquisses
' ----------------------------------------------------------------------------------------------
' Ouvre une esquisse dans le plan (point o, normale n) : plan de base s'il convient, sinon plan cree
Function OuvrirEsquisse(o() As Double, n() As Double, numero As Long) As Boolean
    Dim k As Long, ordre(2) As Long, i As Long
    OuvrirEsquisse = False
    k = AxeDe(n)
    If k > 0 And Abs(o(0) * n(0) + o(1) * n(1) + o(2) * n(2)) < 0.00001 Then
        OrdrePlans k, ordre
        For i = 0 To 2
            If OuvrirSur(gPlan(ordre(i)), o, n) Then
                OuvrirEsquisse = True
                Exit Function
            End If
        Next i
        Exit Function
    End If
    OuvrirEsquisse = CreerPlan(o, n, k, numero)
End Function

' Plans de base dans l'ordre le plus probable pour une normale le long de l'axe k (1 = X, 2 = Y, 3 = Z)
Sub OrdrePlans(k As Long, ordre() As Long)
    Select Case k
        Case 3: ordre(0) = 1: ordre(1) = 2: ordre(2) = 3      ' plan de face
        Case 2: ordre(0) = 2: ordre(1) = 1: ordre(2) = 3      ' plan de dessus
        Case Else: ordre(0) = 3: ordre(1) = 1: ordre(2) = 2   ' plan de droite
    End Select
End Sub

Function AxeDe(n() As Double) As Long
    AxeDe = 0
    If Abs(n(0)) > 0.999999 Then AxeDe = 1
    If Abs(n(1)) > 0.999999 Then AxeDe = 2
    If Abs(n(2)) > 0.999999 Then AxeDe = 3
End Function

' Deux vecteurs unitaires u, v du plan de normale n
Sub Perpendiculaires(n() As Double, u() As Double, v() As Double)
    Dim d As Double, l As Double, k As Long
    If Abs(n(0)) < 0.9 Then
        u(0) = 1: u(1) = 0: u(2) = 0
    Else
        u(0) = 0: u(1) = 1: u(2) = 0
    End If
    d = u(0) * n(0) + u(1) * n(1) + u(2) * n(2)
    For k = 0 To 2
        u(k) = u(k) - d * n(k)
    Next k
    l = Sqr(u(0) * u(0) + u(1) * u(1) + u(2) * u(2))
    For k = 0 To 2
        u(k) = u(k) / l
    Next k
    v(0) = n(1) * u(2) - n(2) * u(1)
    v(1) = n(2) * u(0) - n(0) * u(2)
    v(2) = n(0) * u(1) - n(1) * u(0)
End Sub

' Ouvre une esquisse sur le plan donne et verifie qu'il s'agit bien du plan (o, n)
Function OuvrirSur(plan As Object, o() As Double, n() As Double) As Boolean
    Dim u(2) As Double, v(2) As Double, q As Variant
    Dim k As Long, avant As Long, bon As Boolean, garde As Long
    OuvrirSur = False
    If plan Is Nothing Then Exit Function
    Perpendiculaires n, u, v
    avant = swModel.GetFeatureCount
    swModel.ClearSelection2 True
    plan.Select2 False, 0
    swSkMgr.InsertSketch True
    Set gSk = swSkMgr.ActiveSketch
    If gSk Is Nothing Then Exit Function
    Set gXf = gSk.ModelToSketchTransform
    gAlerte = ""
    LireTransformation
    bon = True
    Dim q0 As Variant, qu As Variant, qv As Variant, du As Double, dv As Double
    q0 = VersEsquisse(o(0), o(1), o(2))
    qu = VersEsquisse(o(0) + 10 * u(0), o(1) + 10 * u(1), o(2) + 10 * u(2))
    qv = VersEsquisse(o(0) + 10 * v(0), o(1) + 10 * v(1), o(2) + 10 * v(2))
    If Abs(q0(2)) > 0.0000002 Or Abs(qu(2)) > 0.0000002 Or Abs(qv(2)) > 0.0000002 Then bon = False
    du = Sqr((qu(0) - q0(0)) ^ 2 + (qu(1) - q0(1)) ^ 2) * 1000#
    dv = Sqr((qv(0) - q0(0)) ^ 2 + (qv(1) - q0(1)) ^ 2) * 1000#
    If Abs(du - 10#) > 0.01 Or Abs(dv - 10#) > 0.01 Then
        gAlerte = "TRANSFORMATION SUSPECTE : 10 mm modele donnent " & Format$(du, "0.000") & " et " & Format$(dv, "0.000") & " mm dans l'esquisse. "
    End If
    If bon Then
        OuvrirSur = True
        Exit Function
    End If
    swSkMgr.InsertSketch True                      ' mauvais plan : refermer l'esquisse vide
    Set gSk = Nothing
    swModel.ClearSelection2 True
    Do While swModel.GetFeatureCount > avant And garde < 3
        Supprimer swModel.FeatureByPositionReverse(0)
        garde = garde + 1
    Loop
End Function

' Cree un plan de reference (o, n) et y ouvre une esquisse. Plusieurs methodes, chacune verifiee.
Function CreerPlan(o() As Double, n() As Double, k As Long, numero As Long) As Boolean
    Dim u(2) As Double, v(2) As Double, dist As Double
    Dim ordre(2) As Long, i As Long, inv As Long, methode As Long
    Dim f As Object, sk3 As Object, p1 As Object, p2 As Object, p3 As Object, ln As Object, sd As Object
    Dim avant As Long, garde As Long

    CreerPlan = False
    Perpendiculaires n, u, v

    ' methode 1 : plan parallele a un plan de base, a la distance voulue
    If k > 0 Then
        dist = Abs(o(0) * n(0) + o(1) * n(1) + o(2) * n(2))
        OrdrePlans k, ordre
        For inv = 0 To 1
            For i = 0 To 2
                swModel.ClearSelection2 True
                gPlan(ordre(i)).Select2 False, 0
                Set f = Nothing
                On Error Resume Next
                Set f = swFeatMgr.InsertRefPlane(8 + 256 * inv, dist * MM, 0, 0#, 0, 0#)
                Err.Clear
                On Error GoTo 0
                If Not f Is Nothing Then
                    If OuvrirSur(f, o, n) Then
                        f.Name = "Plan_" & Format$(numero, "00")
                        CreerPlan = True
                        Exit Function
                    End If
                    Supprimer f
                End If
            Next i
        Next inv
    End If

    ' methode 2 : plan par trois points d'une esquisse 3D ; methode 3 : plan perpendiculaire a une ligne
    For methode = 2 To 3
        avant = swModel.GetFeatureCount
        swModel.ClearSelection2 True
        Set f = Nothing
        On Error Resume Next
        swSkMgr.Insert3DSketch True
        If methode = 2 Then
            Set p1 = swSkMgr.CreatePoint(o(0) * MM, o(1) * MM, o(2) * MM)
            Set p2 = swSkMgr.CreatePoint((o(0) + 20 * u(0)) * MM, (o(1) + 20 * u(1)) * MM, (o(2) + 20 * u(2)) * MM)
            Set p3 = swSkMgr.CreatePoint((o(0) + 20 * v(0)) * MM, (o(1) + 20 * v(1)) * MM, (o(2) + 20 * v(2)) * MM)
        Else
            Set ln = swSkMgr.CreateLine(o(0) * MM, o(1) * MM, o(2) * MM, _
                                        (o(0) + 20 * n(0)) * MM, (o(1) + 20 * n(1)) * MM, (o(2) + 20 * n(2)) * MM)
            Set p1 = ln.GetStartPoint2
        End If
        swSkMgr.Insert3DSketch True
        swModel.ClearSelection2 True
        Set sk3 = swModel.FeatureByPositionReverse(0)
        Set sd = swModel.SelectionManager.CreateSelectData
        If methode = 2 Then
            sd.Mark = 0: p1.Select4 True, sd
            sd.Mark = 1: p2.Select4 True, sd
            sd.Mark = 2: p3.Select4 True, sd
            Set f = swFeatMgr.InsertRefPlane(4, 0#, 4, 0#, 4, 0#)
        Else
            sd.Mark = 0: ln.Select4 True, sd
            sd.Mark = 1: p1.Select4 True, sd
            Set f = swFeatMgr.InsertRefPlane(2, 0#, 4, 0#, 0, 0#)
        End If
        Err.Clear
        On Error GoTo 0
        If Not f Is Nothing Then
            If OuvrirSur(f, o, n) Then
                f.Name = "Plan_" & Format$(numero, "00")
                CreerPlan = True
                Exit Function
            End If
            Supprimer f
        End If
        garde = 0
        Do While swModel.GetFeatureCount > avant And garde < 3     ' retirer l'esquisse 3D inutile
            Supprimer swModel.FeatureByPositionReverse(0)
            garde = garde + 1
        Loop
    Next methode
End Function

' Lit la transformation modele -> esquisse de l'esquisse ouverte (gXf)
Sub LireTransformation()
    Dim q As Variant, k As Long
    gXinfo = ""
    For k = 0 To 8
        gR(k) = 0
    Next k
    gR(0) = 1: gR(4) = 1: gR(8) = 1
    For k = 0 To 2
        gT(k) = 0
    Next k
    gS = 1
    On Error Resume Next
    q = gXf.ArrayData
    If Err.Number = 0 Then
        For k = 0 To 8
            gR(k) = q(k)
        Next k
        For k = 0 To 2
            gT(k) = q(9 + k)
        Next k
        If q(12) <> 0 Then gS = q(12)
        For k = LBound(q) To UBound(q)
            gXinfo = gXinfo & Format$(q(k), "0.####") & " "
        Next k
    End If
    Err.Clear
    On Error GoTo 0
End Sub

' Calibre une fois la convention de la matrice sur le plan de dessus : l'esquisse y a pour axes
' x = X du modele et y = -Z du modele (le Z du modele pointe vers le bas dans la vue de dessus)
Sub Calibrer()
    Dim f As Object, colonne As Boolean, ligne As Boolean
    If gCalibre Then Exit Sub
    gCalibre = True
    gRow = False
    If gPlan(2) Is Nothing Then Exit Sub
    swModel.ClearSelection2 True
    gPlan(2).Select2 False, 0
    swSkMgr.InsertSketch True
    Set gSk = swSkMgr.ActiveSketch
    If gSk Is Nothing Then
        Print #gJournal, "  calibration impossible (esquisse non creee sur le plan de dessus)"
        Exit Sub
    End If
    Set gXf = gSk.ModelToSketchTransform
    LireTransformation
    swSkMgr.InsertSketch True
    Set gSk = Nothing
    Set f = swModel.FeatureByPositionReverse(0)
    If Not f Is Nothing Then
        If f.GetTypeName2 = "ProfileFeature" Then Supprimer f
    End If
    colonne = (Abs(gR(0) - 1) < 0.000001 And Abs(gR(3)) < 0.000001 And Abs(gR(2)) < 0.000001 And Abs(gR(5) + 1) < 0.000001)
    ligne = (Abs(gR(0) - 1) < 0.000001 And Abs(gR(1)) < 0.000001 And Abs(gR(6)) < 0.000001 And Abs(gR(7) + 1) < 0.000001)
    If colonne Then
        gRow = False
        Print #gJournal, "  calibration : matrice par colonnes (plan de dessus : " & gXinfo & ")"
    ElseIf ligne Then
        gRow = True
        Print #gJournal, "  calibration : matrice par lignes (plan de dessus : " & gXinfo & ")"
    Else
        Print #gJournal, "  calibration : AUCUNE convention ne correspond au plan de dessus attendu (" & gXinfo & "), convention par colonnes gardee"
    End If
End Sub

' Point du modele (mm) -> coordonnees dans l'esquisse ouverte (m), calcule avec la matrice de gXf
Function VersEsquisse(x As Double, y As Double, z As Double) As Variant
    Dim px As Double, py As Double, pz As Double, r(2) As Double
    px = x * MM: py = y * MM: pz = z * MM
    If gRow Then
        r(0) = gR(0) * px + gR(3) * py + gR(6) * pz
        r(1) = gR(1) * px + gR(4) * py + gR(7) * pz
        r(2) = gR(2) * px + gR(5) * py + gR(8) * pz
    Else
        r(0) = gR(0) * px + gR(1) * py + gR(2) * pz
        r(1) = gR(3) * px + gR(4) * py + gR(5) * pz
        r(2) = gR(6) * px + gR(7) * py + gR(8) * pz
    End If
    r(0) = r(0) * gS + gT(0)
    r(1) = r(1) * gS + gT(1)
    r(2) = r(2) * gS + gT(2)
    VersEsquisse = r
End Function

' Trace les contours : L segment, C cercle, A arc par trois points, S courbe passant par des points
Sub Dessiner(lignes() As String, i0 As Long, i1 As Long)
    Dim i As Long, t() As String, a As Variant, b As Variant, c As Variant
    Dim n As Long, k As Long, pts() As Double, vp As Variant, seg As Object
    Dim x1 As Double, y1 As Double, x2 As Double, y2 As Double, x3 As Double, y3 As Double
    gTraces = 0: gRefus = 0
    For i = i0 To i1
        If Len(lignes(i)) > 2 Then
            t = Split(lignes(i), " ")
            Select Case t(0)
                Case "L"
                    a = VersEsquisse(Val(t(1)), Val(t(2)), Val(t(3)))
                    b = VersEsquisse(Val(t(4)), Val(t(5)), Val(t(6)))
                    x1 = a(0): y1 = a(1): x2 = b(0): y2 = b(1)
                    Set seg = Nothing
                    Set seg = swSkMgr.CreateLine(x1, y1, 0#, x2, y2, 0#)
                    If seg Is Nothing And InStr(gAlerte, "ligne refusee") = 0 Then
                        gAlerte = gAlerte & "ligne refusee : (" & Format$(x1 * 1000#, "0.000") & " ; " & Format$(y1 * 1000#, "0.000") & _
                                  ") -> (" & Format$(x2 * 1000#, "0.000") & " ; " & Format$(y2 * 1000#, "0.000") & ") mm, donnees " & lignes(i) & ". "
                    End If
                    Compter seg
                Case "C"
                    a = VersEsquisse(Val(t(1)), Val(t(2)), Val(t(3)))
                    x1 = a(0): y1 = a(1)
                    Set seg = Nothing
                    Set seg = swSkMgr.CreateCircleByRadius(x1, y1, 0#, Val(t(4)) * MM)
                    If InStr(gAlerte, "cercle en") = 0 Then
                        gAlerte = gAlerte & "cercle en (" & Format$(x1 * 1000#, "0.000") & " ; " & Format$(y1 * 1000#, "0.000") & ") mm, donnees " & lignes(i) & ". "
                    End If
                    Compter seg
                Case "A"
                    a = VersEsquisse(Val(t(1)), Val(t(2)), Val(t(3)))
                    b = VersEsquisse(Val(t(4)), Val(t(5)), Val(t(6)))
                    c = VersEsquisse(Val(t(7)), Val(t(8)), Val(t(9)))
                    x1 = a(0): y1 = a(1): x2 = b(0): y2 = b(1): x3 = c(0): y3 = c(1)
                    Set seg = Nothing
                    Set seg = swSkMgr.Create3PointArc(x1, y1, 0#, x2, y2, 0#, x3, y3, 0#)
                    Compter seg
                Case "S"
                    n = CLng(Val(t(1)))
                    ReDim pts(3 * n - 1)
                    For k = 0 To n - 1
                        a = VersEsquisse(Val(t(2 + 3 * k)), Val(t(3 + 3 * k)), Val(t(4 + 3 * k)))
                        pts(3 * k) = a(0): pts(3 * k + 1) = a(1): pts(3 * k + 2) = 0#
                    Next k
                    vp = pts
                    Set seg = Nothing
                    On Error Resume Next
                    Set seg = swSkMgr.CreateSpline2(vp, False)
                    If seg Is Nothing Then
                        Err.Clear
                        Set seg = swSkMgr.CreateSpline(vp)
                    End If
                    Err.Clear
                    On Error GoTo 0
                    Compter seg
            End Select
        End If
    Next i
End Sub

Sub Compter(seg As Object)
    If seg Is Nothing Then gRefus = gRefus + 1 Else gTraces = gTraces + 1
End Sub

' Referme l'esquisse ouverte, la nomme et la renvoie (Nothing si elle est vide)
Function FermerEsquisse(nom As String) As Object
    Dim f As Object
    Set FermerEsquisse = Nothing
    swSkMgr.InsertSketch True
    Set gSk = Nothing
    swModel.ClearSelection2 True
    Set f = swModel.FeatureByPositionReverse(0)
    If f Is Nothing Then Exit Function
    If f.GetTypeName2 <> "ProfileFeature" Then Exit Function
    f.Name = nom
    Set FermerEsquisse = f
End Function

Sub Renommer(ancien As String, nouveau As String)
    Dim f As Object
    On Error Resume Next
    Set f = swModel.FeatureByName(ancien)
    If Not f Is Nothing Then f.Name = nouveau
    On Error GoTo 0
End Sub

Sub Supprimer(f As Object)
    If f Is Nothing Then Exit Sub
    On Error Resume Next
    swModel.ClearSelection2 True
    f.Select2 False, 0
    swModel.Extension.DeleteSelection2 0           ' 0 : garde l'esquisse de la fonction supprimee
    swModel.ClearSelection2 True
    Err.Clear
    On Error GoTo 0
End Sub

' ----------------------------------------------------------------------------------------------
'  Controle : volume et centre de gravite de la piece apres la fonction
' ----------------------------------------------------------------------------------------------
Sub Mesurer(ByRef v As Double, m() As Double)
    Dim mp As Object, c As Variant, k As Long
    v = 0
    For k = 0 To 2
        m(k) = 0
    Next k
    On Error Resume Next
    Set mp = Nothing
    Set mp = swModel.Extension.CreateMassProperty2
    If mp Is Nothing Then
        Err.Clear
        Set mp = swModel.Extension.CreateMassProperty
    End If
    If Not mp Is Nothing Then
        mp.UseSystemUnits = True
        v = mp.Volume * 1000000000#                ' m3 -> mm3
        c = mp.CenterOfMass
        If Err.Number = 0 And IsArray(c) Then
            For k = 0 To 2
                m(k) = v * c(k) * 1000#            ' moment statique, mm4
            Next k
        Else
            v = 0
        End If
    End If
    Err.Clear
    On Error GoTo 0
End Sub

' La fonction qui vient d'etre creee a-t-elle change la piece comme attendu ?
' (comparaison des variations de volume et de moment statique, pour pouvoir continuer apres un echec)
Function Conforme(Ve As Double, Ge() As Double, tolV As Double, tolG As Double, ByRef verifiable As Boolean) As Boolean
    Dim Va As Double, Ma(2) As Double, dVa As Double, dVe As Double, k As Long, ecart As Double
    Conforme = False
    Mesurer Va, Ma
    dVa = Va - gVa
    dVe = Ve - gVe
    gDerDV = dVa
    verifiable = (tolV < 0.5 * Abs(dVe))
    If Abs(dVa - dVe) > tolV Then Exit Function
    If Abs(dVe) > 0.01 And (Abs(dVa) < 0.2 * Abs(dVe) Or dVa * dVe < 0) Then Exit Function
    For k = 0 To 2
        ecart = (Ma(k) - gMa(k)) - (Ve * Ge(k) - gMe(k))
        If Abs(ecart) > tolG * Ve + 0.001 Then Exit Function
    Next k
    Conforme = True
    gVa = Va
    gVmes = Va
    For k = 0 To 2
        gMa(k) = Ma(k)
    Next k
End Function
