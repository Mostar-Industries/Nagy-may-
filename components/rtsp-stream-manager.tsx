"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Badge } from "@/components/ui/badge"
import type { RTSPStream } from "@/lib/rtsp-streams"
import { getStreams, saveStream, deleteStream, updateStreamStatus } from "@/lib/rtsp-streams"

export function RTSPStreamManager() {
  const [streams, setStreams] = useState<RTSPStream[]>(getStreams())
  const [isAddingStream, setIsAddingStream] = useState(false)
  const [formData, setFormData] = useState<Partial<RTSPStream>>({
    type: "custom",
    enabled: true,
  })

  const handleAddStream = () => {
    if (!formData.name || !formData.url) {
      alert("Please fill in name and URL")
      return
    }

    const newStream: RTSPStream = {
      id: `custom_${Date.now()}`,
      name: formData.name,
      url: formData.url,
      enabled: formData.enabled ?? true,
      location: {
        lat: Number(formData.location?.lat) || 0,
        lon: Number(formData.location?.lon) || 0,
        name: formData.location?.name || "Custom Location",
      },
      region: formData.region || "Unknown",
      type: formData.type || "custom",
    }

    saveStream(newStream)
    setStreams(getStreams())
    setFormData({ type: "custom", enabled: true })
    setIsAddingStream(false)
  }

  const handleToggle = (id: string) => {
    updateStreamStatus(id, !streams.find((s) => s.id === id)?.enabled)
    setStreams(getStreams())
  }

  const handleDelete = (id: string) => {
    if (confirm("Delete this stream?")) {
      deleteStream(id)
      setStreams(getStreams())
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">RTSP Streams</h2>
        <Dialog open={isAddingStream} onOpenChange={setIsAddingStream}>
          <DialogTrigger asChild>
            <Button size="sm">Add Stream</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add RTSP Stream</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium">Stream Name</label>
                <Input
                  value={formData.name || ""}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g., My Trap Camera"
                />
              </div>
              <div>
                <label className="text-sm font-medium">RTSP URL</label>
                <Input
                  value={formData.url || ""}
                  onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                  placeholder="rtsp://..."
                />
              </div>
              <div>
                <label className="text-sm font-medium">Type</label>
                <Select
                  value={formData.type || "custom"}
                  onValueChange={(value) => setFormData({ ...formData, type: value as any })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="custom">Custom</SelectItem>
                    <SelectItem value="wildlife">Wildlife</SelectItem>
                    <SelectItem value="urban">Urban</SelectItem>
                    <SelectItem value="lab">Lab</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="flex gap-2">
                <div className="flex-1">
                  <label className="text-sm font-medium">Latitude</label>
                  <Input
                    type="number"
                    value={formData.location?.lat || ""}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        location: {
                          ...formData.location,
                          lat: Number(e.target.value),
                        } as any,
                      })
                    }
                    placeholder="0.0"
                  />
                </div>
                <div className="flex-1">
                  <label className="text-sm font-medium">Longitude</label>
                  <Input
                    type="number"
                    value={formData.location?.lon || ""}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        location: {
                          ...formData.location,
                          lon: Number(e.target.value),
                        } as any,
                      })
                    }
                    placeholder="0.0"
                  />
                </div>
              </div>
              <Button onClick={handleAddStream} className="w-full">
                Add Stream
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
        {streams.map((stream) => (
          <Card key={stream.id}>
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <CardTitle className="text-base">{stream.name}</CardTitle>
                  <p className="text-xs text-muted-foreground">{stream.location.name}</p>
                </div>
                <Badge variant={stream.enabled ? "default" : "outline"}>{stream.enabled ? "Active" : "Inactive"}</Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="break-all text-xs font-mono text-muted-foreground">{stream.url}</p>
              <div className="flex items-center gap-2">
                <Checkbox checked={stream.enabled} onCheckedChange={() => handleToggle(stream.id)} />
                <label className="text-sm">Enable stream</label>
              </div>
              <div className="flex gap-2">
                <Button size="sm" variant="outline" onClick={() => handleDelete(stream.id)} className="w-full">
                  Delete
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
