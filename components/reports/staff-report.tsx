"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Star, TrendingUp, Clock } from "lucide-react"

interface StaffReportProps {
  data: any
}

export function StaffReport({ data }: StaffReportProps) {
  if (!data) return null

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Staff Performance Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {data.performance.map((staff: any) => (
              <div key={staff.id} className="flex items-start gap-4 rounded-lg border p-4">
                <Avatar className="h-12 w-12">
                  <AvatarFallback className="bg-primary/10 text-primary">
                    {staff.name
                      .split(" ")
                      .map((n: string) => n[0])
                      .join("")}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1 space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-semibold">{staff.name}</p>
                      <p className="text-sm text-muted-foreground capitalize">{staff.role}</p>
                    </div>
                    <Badge variant={staff.performance === "excellent" ? "default" : "secondary"}>
                      {staff.performance}
                    </Badge>
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    <div className="space-y-1">
                      <div className="flex items-center gap-1 text-sm text-muted-foreground">
                        <TrendingUp className="h-3 w-3" />
                        Orders Served
                      </div>
                      <p className="text-lg font-semibold">{staff.ordersServed}</p>
                    </div>

                    <div className="space-y-1">
                      <div className="flex items-center gap-1 text-sm text-muted-foreground">
                        <Star className="h-3 w-3" />
                        Avg Rating
                      </div>
                      <p className="text-lg font-semibold">{staff.rating.toFixed(1)}/5.0</p>
                    </div>

                    <div className="space-y-1">
                      <div className="flex items-center gap-1 text-sm text-muted-foreground">
                        <Clock className="h-3 w-3" />
                        Avg Time
                      </div>
                      <p className="text-lg font-semibold">{staff.avgServiceTime}m</p>
                    </div>
                  </div>

                  <div className="space-y-1">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Revenue Generated</span>
                      <span className="font-medium">KES {staff.revenue.toLocaleString()}</span>
                    </div>
                    <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
                      <div
                        className="h-full bg-primary transition-all"
                        style={{ width: `${(staff.revenue / data.maxRevenue) * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Top Performers</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {data.topPerformers.map((staff: any, index: number) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-sm font-semibold text-primary">
                      {index + 1}
                    </div>
                    <div>
                      <p className="font-medium">{staff.name}</p>
                      <p className="text-sm text-muted-foreground">{staff.metric}</p>
                    </div>
                  </div>
                  <Star className="h-5 w-5 fill-primary text-primary" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Shift Coverage</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {data.shiftCoverage.map((shift: any) => (
                <div key={shift.shift} className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium">{shift.shift}</span>
                    <span className="text-muted-foreground">{shift.staff} staff</span>
                  </div>
                  <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
                    <div className="h-full bg-primary transition-all" style={{ width: `${shift.coverage}%` }} />
                  </div>
                  <p className="text-xs text-muted-foreground">{shift.coverage}% coverage</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
