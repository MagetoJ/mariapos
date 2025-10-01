"use client"

import { useEffect, useState } from "react"
import { AppLayout } from "@/components/layout/app-layout"
import { tableService, userService } from "@/lib/api/data-service"
import type { Table, User } from "@/lib/types"
import { Button } from "@/components/ui/button"
import { TableGrid } from "@/components/tables/table-grid"
import { TableDetailsDialog } from "@/components/tables/table-details-dialog"
import { ReservationDialog } from "@/components/tables/reservation-dialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Calendar } from "lucide-react"

export default function TablesPage() {
  const [tables, setTables] = useState<Table[]>([])
  const [waiters, setWaiters] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedTable, setSelectedTable] = useState<Table | null>(null)
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false)
  const [reservationDialogOpen, setReservationDialogOpen] = useState(false)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [tablesData, usersData] = await Promise.all([
        tableService.getTables(),
        userService.getUsers(),
      ])
      setTables(tablesData)
      setWaiters(usersData.filter((u) => u.role === "waiter"))
    } catch (err: any) {
      console.error("❌ Failed to fetch data:", err)
      setError(err.message || "Failed to fetch data from server")
      setTables([])
      setWaiters([])
    } finally {
      setLoading(false)
    }
  }

  const handleUpdateTable = async (tableId: string, updates: Partial<Table>) => {
    try {
      const updatedTable = await tableService.updateTable(tableId, updates)
      setTables((prev) => prev.map((t) => (t.id === tableId ? updatedTable : t)))
      if (selectedTable?.id === tableId) {
        setSelectedTable(updatedTable)
      }
    } catch (err) {
      console.error("❌ Failed to update table:", err)
    }
  }

  const handleTableClick = (table: Table) => {
    setSelectedTable(table)
    setDetailsDialogOpen(true)
  }

  const handleReserveClick = (table: Table) => {
    setSelectedTable(table)
    setReservationDialogOpen(true)
  }

  const availableTables = tables.filter((t) => t.status === "available")
  const occupiedTables = tables.filter((t) => t.status === "occupied")
  const reservedTables = tables.filter((t) => t.status === "reserved")
  const cleaningTables = tables.filter((t) => t.status === "cleaning")
  const sections = [...new Set(tables.map((t) => t.section).filter(Boolean))] as string[]

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading tables...</p>
          </div>
        </div>
      </AppLayout>
    )
  }

  if (error) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-full">
          <div className="text-center text-red-600">
            <p className="mb-2 font-bold">Error</p>
            <p>{error}</p>
          </div>
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold tracking-tight text-balance">Table Management</h2>
            <p className="text-muted-foreground">Manage table availability and assignments</p>
          </div>
          <Button onClick={() => setReservationDialogOpen(true)}>
            <Calendar className="mr-2 h-4 w-4" />
            New Reservation
          </Button>
        </div>

        {/* Status Summary */}
        <div className="grid gap-4 md:grid-cols-4">
          <div className="rounded-lg border bg-card p-4">
            <p className="text-sm font-medium text-muted-foreground">Available</p>
            <p className="text-2xl font-bold text-green-600">{availableTables.length}</p>
          </div>
          <div className="rounded-lg border bg-card p-4">
            <p className="text-sm font-medium text-muted-foreground">Occupied</p>
            <p className="text-2xl font-bold text-blue-600">{occupiedTables.length}</p>
          </div>
          <div className="rounded-lg border bg-card p-4">
            <p className="text-sm font-medium text-muted-foreground">Reserved</p>
            <p className="text-2xl font-bold text-purple-600">{reservedTables.length}</p>
          </div>
          <div className="rounded-lg border bg-card p-4">
            <p className="text-sm font-medium text-muted-foreground">Cleaning</p>
            <p className="text-2xl font-bold text-orange-600">{cleaningTables.length}</p>
          </div>
        </div>

        <Tabs defaultValue="all" className="space-y-4">
          <TabsList>
            <TabsTrigger value="all">All Tables ({tables.length})</TabsTrigger>
            <TabsTrigger value="available">Available ({availableTables.length})</TabsTrigger>
            <TabsTrigger value="occupied">Occupied ({occupiedTables.length})</TabsTrigger>
            <TabsTrigger value="reserved">Reserved ({reservedTables.length})</TabsTrigger>
            {sections.map((section) => (
              <TabsTrigger key={section} value={section}>
                {section} ({tables.filter((t) => t.section === section).length})
              </TabsTrigger>
            ))}
          </TabsList>

          <TabsContent value="all">
            <TableGrid
              tables={tables}
              waiters={waiters}
              onTableClick={handleTableClick}
              onReserveClick={handleReserveClick}
              onUpdateTable={handleUpdateTable}
            />
          </TabsContent>

          <TabsContent value="available">
            <TableGrid
              tables={availableTables}
              waiters={waiters}
              onTableClick={handleTableClick}
              onReserveClick={handleReserveClick}
              onUpdateTable={handleUpdateTable}
            />
          </TabsContent>

          <TabsContent value="occupied">
            <TableGrid
              tables={occupiedTables}
              waiters={waiters}
              onTableClick={handleTableClick}
              onReserveClick={handleReserveClick}
              onUpdateTable={handleUpdateTable}
            />
          </TabsContent>

          <TabsContent value="reserved">
            <TableGrid
              tables={reservedTables}
              waiters={waiters}
              onTableClick={handleTableClick}
              onReserveClick={handleReserveClick}
              onUpdateTable={handleUpdateTable}
            />
          </TabsContent>

          {sections.map((section) => (
            <TabsContent key={section} value={section}>
              <TableGrid
                tables={tables.filter((t) => t.section === section)}
                waiters={waiters}
                onTableClick={handleTableClick}
                onReserveClick={handleReserveClick}
                onUpdateTable={handleUpdateTable}
              />
            </TabsContent>
          ))}
        </Tabs>
      </div>

      <TableDetailsDialog
        open={detailsDialogOpen}
        onOpenChange={setDetailsDialogOpen}
        table={selectedTable}
        waiters={waiters}
        onUpdateTable={handleUpdateTable}
      />

      <ReservationDialog
        open={reservationDialogOpen}
        onOpenChange={setReservationDialogOpen}
        table={selectedTable}
        tables={availableTables}
        onUpdateTable={handleUpdateTable}
      />
    </AppLayout>
  )
}
