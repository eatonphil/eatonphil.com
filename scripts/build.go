package main

import (
	"fmt"
	"os"
	"path"
	"strings"
	"bufio"
	"bytes"
	"html/template"
)

var SECTIONS = []struct{
	name string
	ctx map[string]any
}{
	{
		"notes",
		map[string]any{"Tag": "Notes by a software developer"},
	},
	{
		"letters",
		map[string]any{"Tag": "Letters by a software developer"},
	},
	{
		"lists",
		map[string]any{"Tag": "Phil Eaton's Lists"},
	},
	{
		"home",
		map[string]any{"Tag": "Phil Eaton"},
	},
}

type Doc struct {
	Title string
	Date string
	Tags []string
	Body []byte
	FullUrl string
}

func parseDoc(docPath string) Doc {
	contents, err := os.ReadFile(docPath)
	if err != nil {
		panic(err)
	}

	sections := strings.Split(string(contents), "---")
	header := sections[0]
	body := sections[1]

	var d Doc

	for _, line := range strings.Split(header, "\n") {
		if strings.TrimSpace(line) == "" {
			continue
		}
		parts := strings.Split(line, "=")
		key := strings.TrimSpace(parts[0])
		value := strings.TrimSpace(parts[1])
		switch key {
		case "title":
			d.Title = value
		case "date":
			d.Date = value
		case "tags":
			d.Tags = strings.Split(value, ",")
		}
	}

	var out bytes.Buffer
	outWriter := bufio.NewWriter(&out)
	bodyRunes := []rune(body)
	var prev rune
	var i int
	for i < len(bodyRunes) {
		if i > 0 {
			prev = bodyRunes[i-1]
		}

		c := bodyRunes[i]
		// Deal with headers
		if (i == 0 || prev == '\n') && c == '#' {
			var headerNumber = 0
			for c == '#' {
				i++
				headerNumber++
				c = bodyRunes[i]
			}

			var header []rune
			for !(c == '\r' || c == '\n') {
				i++
				header = append(header, c)
				c = bodyRunes[i]
			}

			fmt.Fprintf(outWriter, "<h%d>%s</hd%>", headerNumber, header, headerNumber)
			continue
		}

		outWriter.WriteRune(c)
		i++
	}
	d.Body = out.Bytes()

	return d
}

func buildSection(t *template.Template, section string, ctx map[string]any) {
	files, err := os.ReadDir(path.Join(section, "posts"))
	if err != nil {
		panic(err)
	}

	for _, f := range files {
		inputPath := path.Join(section, "posts", f.Name())
		fmt.Println("Building", inputPath)
		doc := parseDoc(inputPath)

		outputPath := path.Join(section, "build", f.Name())
		if strings.HasSuffix(f.Name(), ".md") {
			outputPath = outputPath[:len(outputPath)-4] + ".html"
		}

		o, err := os.Open(outputPath)
		if err != nil  {
			panic(err)
		}

		ctx["Page"] = doc
		t.Execute(o, ctx)
	}
}

func main() {
	mailFile, err := os.ReadFile("mail.html")
	if err != nil {
		panic(err)
	}

	t, err := template.New("template").ParseFiles("template.html")
	if err != nil {
		panic(err)
	}
	for _, section := range SECTIONS {
		fmt.Println("Building section", section.name)
		if section.name == "notes" {
			continue
		}

		buildPath := path.Join(os.Cwd(), section.name, "build")
		err := os.RemoveAll(buildPath)
		if err != nil {
			panic(err)
		}

		err := os.MkdirAll(buildPath, os.ModePerm)
		if err != nil {
			panic(err)
		}

		section.ctx["mail"] = mailFile
		buildSection(t, section.name, section.ctx)
	}
}
