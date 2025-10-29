import { z } from "zod"

export const DetectionSchema = z.object({
  latitude: z.number().min(-90).max(90),
  longitude: z.number().min(-180).max(180),
  confidence: z.number().min(0).max(100),
  type: z.enum(["confirmed", "suspected"]),
  description: z.string().min(1).max(1000),
})

export const NoteSchema = z.object({
  title: z.string().min(1).max(255),
  shared: z.boolean().default(false),
})

export const ParagraphSchema = z.object({
  content: z.string().min(1).max(5000),
  note_id: z.string().uuid(),
})

export const UserInputSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(255),
})

export type Detection = z.infer<typeof DetectionSchema>
export type Note = z.infer<typeof NoteSchema>
export type Paragraph = z.infer<typeof ParagraphSchema>
export type UserInput = z.infer<typeof UserInputSchema>
