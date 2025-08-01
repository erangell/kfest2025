; APPLE 2C SERIAL MIDI OUTPUT TO ARDUINO TO YAMAHA EZAG GUITAR
; ASSEMBLE WITH CYANIIDE MERLIN IDE AT https://paleotronic.com/merlinplus
			ORG $6000
DELAY		EQU	$FCA8
PRTHEX		EQU	$FDDA
MAININIT	JMP INITSERIAL	; 6031
			JMP GTRSTRUM	; 608D
			JMP GTRDAMP		; 60BD
			JMP MIDIOUT		; 603C
			JMP SYSXOUT		; 6049
			JMP MIDITEST	; 605D
; 6012
GTRFRETS	DFB $00,$00,$00,$00,$00,$00
STRUMDLY	DFB $81	; DELAY BETWEEN STRINGS WHEN STRUMMING
GTRTUNE		DFB 52,57,62,67,71,76
LIGHTMAX	DFB 58,63,68,73,77,82
SYSEX		DFB $F0,$43,$7F,$00,$00
SYSXLED		DFB $03	; 03 = TURN LED ON, 04 = TURN OFF
SYSXSTRG	DFB $06	; STRING NUMBER: 6 = BASS E, 1 = HIGH E
SYSXNOTE	DFB $35	; MIDI NOTE NUMBER FOR FRET
			DFB $F7
MIDICHNL	DFB $00 ; TO CHANGE MIDI CHANNEL FOR OUTPUT: $602E
MIDIVEL		DFB $40 ; MIDI VELOCITY FOR NOTE ONS: $602F
VELTEMP		DFB $00
MIDIDUMP	DFB $00	; 01 TO DISPLAY MIDI BYTES ON SCREEN - DO NOT SEND
;
INITSERIAL	LDA #$1F	; APPLE 2C SERIAL PORT MAPPED TO SLOT 2
			STA $C0A3
			LDA #$0B
			STA $C0A2
			RTS
MIDIOUT		PHA
			LDA MIDIDUMP
			BNE DUMPMIDI
			LDA #$10
WTREADY		BIT $C0A1
			BEQ WTREADY
			PLA
			STA $C0A0
			RTS
DUMPMIDI	PLA
			JSR PRTHEX
			RTS
SYSXOUT		LDX #$00
			LDA SYSEX,X
SYSXLOOP	JSR MIDIOUT
			INX
			LDA SYSEX,X
			CMP #$F7
			BNE SYSXLOOP
			JSR MIDIOUT
			RTS
MIDITEST	LDA MIDICHNL
			CLC
			ADC #$90
			JSR MIDIOUT
			LDA #$3C	; MIDDLE C
			JSR MIDIOUT
			LDA MIDIVEL
			JSR MIDIOUT
			LDA #$FF
			JSR DELAY
			LDA MIDICHNL
			CLC
			ADC #$90
			JSR MIDIOUT
			LDA #$3C	; MIDDLE C
			JSR MIDIOUT
			LDA #$00	; NOTE OFF
			JSR MIDIOUT
			JSR SYSXOUT
			RTS
GTRSTRUM	LDA MIDIVEL
			STA VELTEMP
STRUM		LDX #$00
STRUMLP		LDA MIDICHNL
			CLC
			ADC #$90
			JSR MIDIOUT
			LDA GTRFRETS,X
			CLC
			ADC GTRTUNE,X
			PHA
			JSR MIDIOUT
			LDA VELTEMP
			JSR MIDIOUT
			PLA
			JSR CHKLIGHT
			LDA STRUMDLY
			JSR	DELAY
			INX
			CPX #$06
			BNE STRUMLP
			RTS
GTRDAMP		LDA #$00
			STA VELTEMP
			JSR STRUM
			RTS
CHKLIGHT	PHA		;deterine if midi note should turn on an LED
			TAY		;save midi note number
			TXA		; X has string number 0-5
			PHA		; save X and A
			TYA
			CMP GTRTUNE,X
			BEQ NOLIGHT	; no light if unfretted note
			CMP LIGHTMAX,X
			BEQ DOLIGHT			
			BCS NOLIGHT	; no light if greater than 6th fret
DOLIGHT		STA SYSXNOTE
			TXA
			EOR #$07	; COMPLEMENT STRING NUMBER TO MAP 0-6 TO 6-1
			SEC
			SBC #$01
			STA SYSXSTRG
			LDA #$03
			STA SYSXLED
			LDA VELTEMP
			BNE DOLED
			INC SYSXLED
DOLED		JSR SYSXOUT
NOLIGHT		PLA
			TAX
			PLA
			RTS
