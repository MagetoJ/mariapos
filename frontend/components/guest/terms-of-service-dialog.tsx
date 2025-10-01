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
// Terms of Service content
const TERMS_OF_SERVICE = `MARIA HAVENS POINT OF SALE SYSTEM - TERMS OF SERVICE

Last Updated: January 1, 2024

1. ACCEPTANCE OF TERMS

By accessing and using the Maria Havens Point of Sale (POS) system, you accept and agree to be bound by the terms and provision of this agreement.

2. DESCRIPTION OF SERVICE

Maria Havens provides a comprehensive point of sale system for restaurant and hospitality businesses, including but not limited to:
- Order management and processing
- Menu and inventory management
- Guest services and reservations
- Payment processing
- Reporting and analytics

3. USER ACCOUNTS

3.1 Account Registration
- Users must provide accurate and complete information when creating accounts
- Users are responsible for maintaining the confidentiality of their account credentials
- Users must immediately notify Maria Havens of any unauthorized use of their account

3.2 Account Types
- Admin: Full system access and management capabilities
- Manager: Limited administrative access for daily operations
- Staff: Basic operational access for order processing and guest services
- Guest: Limited access to personal orders and service requests

4. ACCEPTABLE USE

Users agree to:
- Use the system only for legitimate business purposes
- Comply with all applicable laws and regulations
- Maintain the confidentiality of customer information
- Report any security vulnerabilities or system issues immediately

Users agree NOT to:
- Attempt to gain unauthorized access to any part of the system
- Use the system for any illegal or unauthorized purpose
- Share account credentials with unauthorized individuals
- Reverse engineer or attempt to extract source code

5. PRIVACY AND DATA PROTECTION

5.1 Data Collection
- We collect information necessary for system operation and service provision
- Personal data is processed in accordance with our Privacy Policy
- Customer payment information is processed securely and not stored locally

5.2 Data Security
- We implement industry-standard security measures to protect data
- Users are responsible for maintaining secure passwords and access controls
- Any suspected data breaches must be reported immediately

6. PAYMENT AND BILLING

6.1 Service Fees
- Service fees are outlined in your service agreement
- Fees are subject to change with 30 days' written notice
- Late payments may result in service suspension

6.2 Payment Processing
- Payment processing fees apply as outlined in your merchant agreement
- Maria Havens is not responsible for payment processor fees or policies
- Chargebacks and disputes are handled according to processor policies

7. SERVICE AVAILABILITY

7.1 Uptime
- We strive to maintain 99.9% system uptime
- Scheduled maintenance will be announced in advance
- Emergency maintenance may be performed without notice

7.2 Support
- Technical support is available during business hours
- Emergency support is available for critical system issues
- Response times vary based on issue severity and service level

8. LIMITATION OF LIABILITY

8.1 Service Limitations
- The system is provided "as is" without warranties of any kind
- We do not guarantee uninterrupted or error-free operation
- Users are responsible for maintaining data backups

8.2 Liability Limits
- Our liability is limited to the amount paid for services in the preceding 12 months
- We are not liable for indirect, incidental, or consequential damages
- Users assume responsibility for business decisions based on system data

9. INTELLECTUAL PROPERTY

9.1 System Ownership
- Maria Havens retains all rights to the POS system software and documentation
- Users receive a limited license to use the system according to these terms
- Custom configurations and reports remain the property of Maria Havens

9.2 User Data
- Users retain ownership of their business data entered into the system
- Maria Havens may use aggregated, anonymized data for system improvement
- User data will not be shared with third parties without consent

10. TERMINATION

10.1 Termination by User
- Users may terminate service with 30 days' written notice
- Final invoices must be paid within 30 days of termination
- Data export assistance is available for 90 days after termination

10.2 Termination by Maria Havens
- We may terminate service for breach of these terms
- We may terminate service with 30 days' notice for any reason
- Immediate termination may occur for security violations or non-payment

11. MODIFICATIONS TO TERMS

11.1 Updates
- These terms may be updated periodically
- Users will be notified of significant changes
- Continued use constitutes acceptance of modified terms

11.2 Disputes
- Any disputes will be resolved through binding arbitration
- These terms are governed by the laws of [Your State/Country]
- Court proceedings, if necessary, will be conducted in [Your Jurisdiction]

12. CONTACT INFORMATION

For questions about these terms or the service, please contact:

Maria Havens Support Team
Email: support@mariahavens.com
Phone: 1-800-HAVENS-1
Address: [Your Business Address]

13. ACKNOWLEDGMENT

By clicking "Accept & Continue," you acknowledge that you have read, understood, and agree to be bound by these Terms of Service.`
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
