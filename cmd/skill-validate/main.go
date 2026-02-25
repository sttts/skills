package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"strings"
)

var errors int

func logError(format string, args ...any) {
	fmt.Fprintf(os.Stderr, "ERROR: "+format+"\n", args...)
	errors++
}

func logInfo(format string, args ...any) {
	fmt.Printf("CHECK: "+format+"\n", args...)
}

type MarketplaceJSON struct {
	Plugins []struct {
		Version string `json:"version"`
	} `json:"plugins"`
}

type PluginJSON struct {
	Version string `json:"version"`
}

func readJSON(path string, v any) error {
	data, err := os.ReadFile(path)
	if err != nil {
		return err
	}
	return json.Unmarshal(data, v)
}

func extractFrontmatter(path string) (map[string]string, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()

	result := make(map[string]string)
	scanner := bufio.NewScanner(f)

	// first line must be ---
	if !scanner.Scan() || strings.TrimSpace(scanner.Text()) != "---" {
		return nil, fmt.Errorf("missing YAML frontmatter")
	}

	// read until next ---
	for scanner.Scan() {
		line := scanner.Text()
		if strings.TrimSpace(line) == "---" {
			break
		}
		if idx := strings.Index(line, ":"); idx > 0 {
			key := strings.TrimSpace(line[:idx])
			value := strings.TrimSpace(line[idx+1:])
			value = strings.Trim(value, `"'`)
			result[key] = value
		}
	}
	return result, scanner.Err()
}

func findScriptRefs(path string) ([]string, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	re := regexp.MustCompile(`\$\{CLAUDE_PLUGIN_ROOT\}/([^"'\s]+)`)
	matches := re.FindAllStringSubmatch(string(data), -1)
	var refs []string
	for _, m := range matches {
		refs = append(refs, m[1])
	}
	return refs, nil
}

func main() {
	repoRoot := "."
	if len(os.Args) > 1 {
		repoRoot = os.Args[1]
	}
	repoRoot, _ = filepath.Abs(repoRoot)

	// read marketplace.json
	marketplacePath := filepath.Join(repoRoot, ".claude-plugin", "marketplace.json")
	var marketplace MarketplaceJSON
	if err := readJSON(marketplacePath, &marketplace); err != nil {
		logError("%s: %v", marketplacePath, err)
		os.Exit(1)
	}
	if len(marketplace.Plugins) == 0 {
		logError("%s: no plugins defined", marketplacePath)
		os.Exit(1)
	}
	expectedVersion := marketplace.Plugins[0].Version
	logInfo("Expected version: %s", expectedVersion)

	logInfo("Validating %s", marketplacePath)

	// find all plugins
	pluginsDir := filepath.Join(repoRoot, "plugins")
	entries, err := os.ReadDir(pluginsDir)
	if err != nil {
		logError("Cannot read plugins directory: %v", err)
		os.Exit(1)
	}

	for _, entry := range entries {
		if !entry.IsDir() {
			continue
		}
		pluginName := entry.Name()
		pluginDir := filepath.Join(pluginsDir, pluginName)
		logInfo("Validating plugin: %s", pluginName)

		// check plugin.json
		pluginJSONPath := filepath.Join(pluginDir, ".claude-plugin", "plugin.json")
		var plugin PluginJSON
		if err := readJSON(pluginJSONPath, &plugin); err != nil {
			logError("%s: %v", pluginJSONPath, err)
			continue
		}
		if plugin.Version != expectedVersion {
			logError("%s version (%s) doesn't match expected (%s)", pluginJSONPath, plugin.Version, expectedVersion)
		}

		// check all SKILL.md files
		skillsDir := filepath.Join(pluginDir, "skills")
		skillEntries, _ := os.ReadDir(skillsDir)
		for _, skillEntry := range skillEntries {
			if !skillEntry.IsDir() {
				continue
			}
			skillName := skillEntry.Name()
			skillFile := filepath.Join(skillsDir, skillName, "SKILL.md")
			if _, err := os.Stat(skillFile); os.IsNotExist(err) {
				continue
			}
			logInfo("  Validating skill: %s", skillName)

			fm, err := extractFrontmatter(skillFile)
			if err != nil {
				logError("%s: %v", skillFile, err)
				continue
			}

			// check required fields
			for _, field := range []string{"name", "description", "version"} {
				if fm[field] == "" {
					logError("%s missing '%s' in frontmatter", skillFile, field)
				}
			}

			// check version matches
			if fm["version"] != "" && fm["version"] != expectedVersion {
				logError("%s version (%s) doesn't match expected (%s)", skillFile, fm["version"], expectedVersion)
			}

			// check script references exist
			refs, _ := findScriptRefs(skillFile)
			for _, ref := range refs {
				fullPath := filepath.Join(pluginDir, ref)
				if _, err := os.Stat(fullPath); os.IsNotExist(err) {
					logError("%s references non-existent: %s", skillFile, ref)
				}
			}
		}

		// check scripts are executable with shebang
		scriptsDir := filepath.Join(pluginDir, "scripts")
		if info, err := os.Stat(scriptsDir); err == nil && info.IsDir() {
			scriptEntries, _ := os.ReadDir(scriptsDir)
			for _, scriptEntry := range scriptEntries {
				if scriptEntry.IsDir() {
					continue
				}
				scriptName := scriptEntry.Name()
				scriptPath := filepath.Join(scriptsDir, scriptName)
				logInfo("  Validating script: %s", scriptName)

				info, err := os.Stat(scriptPath)
				if err != nil {
					logError("%s: %v", scriptPath, err)
					continue
				}
				if info.Mode()&0111 == 0 {
					logError("%s is not executable", scriptPath)
				}

				// check shebang
				f, err := os.Open(scriptPath)
				if err == nil {
					scanner := bufio.NewScanner(f)
					if scanner.Scan() {
						if !strings.HasPrefix(scanner.Text(), "#!") {
							logError("%s missing shebang", scriptPath)
						}
					}
					f.Close()
				}
			}
		}
	}

	fmt.Println()
	if errors > 0 {
		fmt.Printf("FAILED: %d error(s) found\n", errors)
		os.Exit(1)
	}
	fmt.Println("PASSED: All checks passed")
}
