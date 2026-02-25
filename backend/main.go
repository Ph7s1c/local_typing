package main

import (
	"log"

	"github.com/pocketbase/pocketbase"
	"github.com/pocketbase/pocketbase/apis"
	"github.com/pocketbase/pocketbase/core"
)

func main() {
    config := pocketbase.Config{
        HideStartBanner: false,
        DefaultDev:      false,
    }

	app := pocketbase.NewWithConfig(config)

    app.OnServe().BindFunc(func(e *core.ServeEvent) error {
        // register new "GET /hello" route
        e.Router.GET("/hello", func(e *core.RequestEvent) error {
            return e.String(200, "Hello world!")
        }).Bind(apis.RequireAuth())
        e.Router.GET("/bye", func(e *core.RequestEvent) error {
            return e.String(200, "Hello world!")
        })

        return e.Next()
    })

	if err := app.Start(); err != nil {
		log.Fatal(err)
	}
}
