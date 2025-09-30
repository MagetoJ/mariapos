"use client"

import type React from "react"

import { useState } from "react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { TERMS_OF_SERVICE } from "@/lib/mock-data/terms-of-service"
import { AlertCircle } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"

interface TermsOfServiceDialogProps {
  open: boolean
  onAccept: () => void
  onDecline: () => void
}

export function TermsOfServiceDialog({ open, onAccept, onDecline }: TermsOfServiceDialogProps) {
  const [hasRead, setHasRead] = useState(false)
  const [hasScrolled, setHasScrolled] = useState(false)

  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const target = e.target as HTMLDivElement
    const bottom = target.scrollHeight - target.scrollTop <= target.clientHeight + 50
    if (bottom) {
      setHasScrolled(true)
    }
  }

  return (
    <Dialog open={open} onOpenChange={() => {}}>
      <DialogContent className="max-w-3xl max-h-[90vh]" onInteractOutside={(e) => e.preventDefault()}>
        <DialogHeader>
          <DialogTitle>Terms of Service</DialogTitle>
          <DialogDescription>
            Please read and accept our terms of service to continue using Maria Havens services.
          </DialogDescription>
        </DialogHeader>

        <ScrollArea className="h-[400px] w-full rounded-md border p-4" onScrollCapture={handleScroll}>
          <div className="prose prose-sm dark:prose-invert max-w-none">
            <div className="whitespace-pre-wrap text-sm">{TERMS_OF_SERVICE}</div>
          </div>
        </ScrollArea>

        {!hasScrolled && (
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>Please scroll to the bottom to read all terms before accepting.</AlertDescription>
          </Alert>
        )}

        <div className="flex items-center space-x-2">
          <Checkbox
            id="terms"
            checked={hasRead}
            onCheckedChange={(checked) => setHasRead(checked === true)}
            disabled={!hasScrolled}
          />
          <Label
            htmlFor="terms"
            className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
          >
            I have read and agree to the Terms of Service
          </Label>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onDecline}>
            Decline
          </Button>
          <Button onClick={onAccept} disabled={!hasRead || !hasScrolled}>
            Accept & Continue
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
