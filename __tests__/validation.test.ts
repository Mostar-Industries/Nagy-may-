import { DetectionSchema, NoteSchema } from "@/lib/validation"

describe("Validation Schemas", () => {
  describe("DetectionSchema", () => {
    it("should validate correct detection data", () => {
      const valid = {
        latitude: 6.5244,
        longitude: 3.3792,
        confidence: 92,
        type: "confirmed" as const,
        description: "Detection in Lagos State",
      }
      expect(() => DetectionSchema.parse(valid)).not.toThrow()
    })

    it("should reject invalid latitude", () => {
      const invalid = {
        latitude: 91,
        longitude: 3.3792,
        confidence: 92,
        type: "confirmed" as const,
        description: "Detection in Lagos State",
      }
      expect(() => DetectionSchema.parse(invalid)).toThrow()
    })

    it("should reject invalid confidence", () => {
      const invalid = {
        latitude: 6.5244,
        longitude: 3.3792,
        confidence: 150,
        type: "confirmed" as const,
        description: "Detection in Lagos State",
      }
      expect(() => DetectionSchema.parse(invalid)).toThrow()
    })
  })

  describe("NoteSchema", () => {
    it("should validate correct note data", () => {
      const valid = {
        title: "Test Note",
        shared: false,
      }
      expect(() => NoteSchema.parse(valid)).not.toThrow()
    })

    it("should reject empty title", () => {
      const invalid = {
        title: "",
        shared: false,
      }
      expect(() => NoteSchema.parse(invalid)).toThrow()
    })
  })
})
